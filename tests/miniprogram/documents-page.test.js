const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

function loadPage() {
  let definition
  global.Page = page => { definition = page }
  global.getApp = () => ({ globalData: { apiBaseUrl: 'http://test/api/v1', user: { role: 'admin' } } })
  global.wx = {
    getStorageSync: () => 'test-token',
    showToast: () => {},
    request: () => {},
    showModal: () => {}
  }
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
