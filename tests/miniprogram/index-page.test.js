const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

test('question page retains cited sources returned by the chat API', async () => {
  let definition
  global.Page = page => { definition = page }
  global.getApp = () => ({ globalData: { apiBaseUrl: 'http://test/api/v1' } })
  global.wx = {
    getStorageSync: () => 'test-token',
    showToast: () => {},
    request: options => options.success({
      statusCode: 200,
      data: {
        answer: '报销需要在三天内提交。',
        sources: [{ name: '报销制度.txt', page: 2, content: '员工须在三天内提交报销申请。' }]
      }
    })
  }

  const requestModule = path.resolve(__dirname, '../../miniprogram/utils/request.js')
  const pageModule = path.resolve(__dirname, '../../miniprogram/pages/index/index.js')
  delete require.cache[requestModule]
  delete require.cache[pageModule]
  require(pageModule)

  const context = {
    data: { question: '报销多久提交？', answer: '', sources: [], loading: false, questionCount: 0 },
    setData(update) { Object.assign(this.data, update) }
  }

  definition.askQuestion.call(context)
  await new Promise(resolve => setImmediate(resolve))

  assert.deepEqual(context.data.sources, [
    { name: '报销制度.txt', page: 2, content: '员工须在三天内提交报销申请。' }
  ])
})

test('homepage loads document overview and exposes document shortcuts', async () => {
  let definition
  const switchTabCalls = []
  global.Page = page => { definition = page }
  global.getApp = () => ({ globalData: { apiBaseUrl: 'http://test/api/v1', user: { role: 'admin' } } })
  global.wx = {
    getStorageSync: () => 'test-token',
    showToast: () => {},
    switchTab: options => switchTabCalls.push(options),
    request: options => options.success({
      statusCode: 200,
      data: { items: [{ id: 'a', name: '制度.txt', chunks: 4 }, { id: 'b', name: '手册.pdf', chunks: 7 }] }
    })
  }

  const requestModule = path.resolve(__dirname, '../../miniprogram/utils/request.js')
  const pageModule = path.resolve(__dirname, '../../miniprogram/pages/index/index.js')
  delete require.cache[requestModule]
  delete require.cache[pageModule]
  require(pageModule)

  const context = {
    data: { documents: [], documentCount: 0, chunkCount: 0, overviewError: '' },
    setData(update) { Object.assign(this.data, update) }
  }
  context.loadOverview = definition.loadOverview
  context.openDocuments = definition.openDocuments
  context.chooseFile = definition.chooseFile

  definition.onShow.call(context)
  await new Promise(resolve => setImmediate(resolve))

  assert.equal(context.data.documentCount, 2)
  assert.equal(context.data.chunkCount, 11)
  assert.equal(context.data.documents[0].name, '制度.txt')
  definition.openDocuments.call(context)
  definition.chooseFile.call(context)
  assert.deepEqual(switchTabCalls, [
    { url: '/pages/documents/index' },
    { url: '/pages/documents/index' }
  ])
})
