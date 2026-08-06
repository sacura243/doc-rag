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
