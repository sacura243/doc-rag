const assert = require('node:assert/strict')
const test = require('node:test')
const fs = require('node:fs')
const path = require('node:path')

test('homepage native buttons explicitly neutralize default padding for centered labels', () => {
  const stylesheet = fs.readFileSync(
    path.resolve(__dirname, '../../miniprogram/pages/index/index.wxss'),
    'utf8'
  )

  for (const selector of ['.ask', '.empty-button']) {
    const rule = stylesheet.match(new RegExp(`\\${selector}\\{([^}]*)\\}`))
    assert.ok(rule, `${selector} rule should exist`)
    assert.match(rule[1], /display:flex/)
    assert.match(rule[1], /align-items:center/)
    assert.match(rule[1], /justify-content:center/)
  }

  assert.match(stylesheet, /\.ask,\.empty-button\{box-sizing:border-box;padding:0\}/)
})

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
  global.getApp = () => ({ globalData: { apiBaseUrl: 'http://test/api/v1', environment: 'production', user: { role: 'admin' } }, login: callback => callback({ role: 'admin' }) })
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

test('production homepage waits for real login before loading documents', () => {
  let definition
  let loginCalls = 0
  let overviewCalls = 0
  global.Page = page => { definition = page }
  global.getApp = () => ({
    globalData: { environment: 'production', user: null },
    login: callback => { loginCalls += 1; callback({ role: 'member' }) }
  })
  global.wx = { showToast: () => {} }

  const pageModule = path.resolve(__dirname, '../../miniprogram/pages/index/index.js')
  delete require.cache[pageModule]
  require(pageModule)

  const context = {
    data: { isAdmin: false },
    setData(update) { Object.assign(this.data, update) },
    loadOverview() { overviewCalls += 1 }
  }

  definition.onShow.call(context)

  assert.equal(loginCalls, 1)
  assert.equal(overviewCalls, 1)
})
