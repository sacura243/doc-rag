const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

function loadPage(globalData = { apiBaseUrl: 'http://test/api/v1', transport: 'http', user: { role: 'admin' } }) {
  let definition
  global.Page = page => { definition = page }
  global.getApp = () => ({ globalData })
  global.wx = {
    getStorageSync: () => 'test-token',
    showToast: () => {},
    request: () => {},
    showModal: () => {}
  }
  const requestModule = require.resolve('../../miniprogram/utils/request')
  delete require.cache[requestModule]
  const modulePath = path.resolve(__dirname, '../../miniprogram/pages/documents/index.js')
  delete require.cache[modulePath]
  require(modulePath)
  return { modulePath, definition }
}

test('document page rejects unsupported and oversized files before upload', () => {
  const loaded = loadPage()
  const pageModule = require(loaded.modulePath)

  assert.equal(pageModule.validateFile({ name: 'notes.exe', size: 10 }), '仅支持 TXT、PDF、DOCX 文件')
  assert.equal(pageModule.validateFile({ name: 'large.pdf', size: 10 * 1024 * 1024 + 1 }), '文件超过 10 MB')
  assert.equal(pageModule.validateFile({ name: 'guide.pdf', size: 10 }), '')
})

test('document page maps API upload errors to user-facing messages', () => {
  const loaded = loadPage()
  const pageModule = require(loaded.modulePath)

  assert.equal(pageModule.formatUploadError(413, { detail: 'Document exceeds 10 MB' }), '文件超过 10 MB')
  assert.equal(pageModule.formatUploadError(415, { detail: 'Unsupported document type' }), '仅支持 TXT、PDF、DOCX 文件')
  assert.equal(pageModule.formatUploadError(500, { detail: '索引服务不可用' }), '索引服务不可用')
})

test('document page completes sequential uploads and refreshes the list', async () => {
  const loaded = loadPage()
  const uploaded = []
  let refreshed = false
  global.wx.uploadFile = options => {
    uploaded.push(options.filePath)
    options.success({ statusCode: 201, data: '{}' })
  }
  const context = {
    data: { uploading: false, uploadProgress: 0, errorMessage: '' },
    setData(update) { Object.assign(this.data, update) },
    uploadSingle: loaded.definition.uploadSingle,
    loadDocuments: () => { refreshed = true }
  }

  loaded.definition.uploadFiles.call(context, [
    { name: 'one.txt', path: 'C:/one.txt', size: 10 },
    { name: 'two.pdf', path: 'C:/two.pdf', size: 10 }
  ])
  await new Promise(resolve => setImmediate(resolve))
  await new Promise(resolve => setImmediate(resolve))

  assert.deepEqual(uploaded, ['C:/one.txt', 'C:/two.pdf'])
  assert.equal(context.data.uploadProgress, 100)
  assert.equal(context.data.uploading, false)
  assert.equal(refreshed, true)
})

test('production upload uses CloudBase storage then imports the temporary URL', async () => {
  const calls = []
  const loaded = loadPage({
    apiBaseUrl: '',
    transport: 'cloud-container',
    cloudEnv: 'prod-d6gkf5lgbb9d67abc',
    cloudService: 'knowledge-api',
    user: { role: 'admin' }
  })
  global.wx.cloud = {
    uploadFile: options => {
      calls.push(['uploadFile', options])
      options.success({ fileID: 'cloud://docs/one.txt' })
    },
    getTempFileURL: options => {
      calls.push(['getTempFileURL', options])
      options.success({ fileList: [{ fileID: 'cloud://docs/one.txt', tempFileURL: 'https://storage.example.com/one.txt' }] })
    },
    deleteFile: options => {
      calls.push(['deleteFile', options])
      options.success({ fileList: [] })
    },
    callContainer: options => {
      calls.push(['callContainer', options])
      options.success({ statusCode: 201, data: { files: 1, chunks: 2, total_chunks: 2 } })
    }
  }
  const context = {
    data: { uploading: false, uploadProgress: 0, errorMessage: '' },
    setData(update) { Object.assign(this.data, update) },
    uploadSingle: loaded.definition.uploadSingle,
    loadDocuments: () => {}
  }

  await context.uploadSingle.call(context, { name: 'one.txt', path: 'C:/one.txt', size: 10 })

  assert.deepEqual(calls.map(([name]) => name), ['uploadFile', 'getTempFileURL', 'callContainer', 'deleteFile'])
  assert.equal(calls[2][1].path, '/api/v1/documents/import-url')
  assert.deepEqual(calls[2][1].data, { url: 'https://storage.example.com/one.txt', filename: 'one.txt' })
})

test('delete encodes document names before calling the CloudBase container', async () => {
  const calls = []
  const loaded = loadPage({
    apiBaseUrl: '',
    transport: 'cloud-container',
    cloudEnv: 'prod-d6gkf5lgbb9d67abc',
    cloudService: 'knowledge-api',
    user: { role: 'admin' }
  })
  global.wx.showModal = options => options.success({ confirm: true })
  global.wx.cloud = {
    callContainer: options => {
      calls.push(options)
      options.success({ statusCode: 200, data: { deleted_chunks: 3 } })
    }
  }
  const context = {
    data: { errorMessage: '' },
    setData(update) { Object.assign(this.data, update) },
    loadDocuments: () => {}
  }

  loaded.definition.deleteDocument.call(context, {
    currentTarget: { dataset: { id: '曾李孟 简历 AI岗_企业知识库版_投递版 (1).pdf' } }
  })
  await new Promise(resolve => setImmediate(resolve))

  assert.equal(calls[0].path, `/api/v1/documents/${encodeURIComponent('曾李孟 简历 AI岗_企业知识库版_投递版 (1).pdf')}`)
})
