const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

test('app login invokes completion callback with the current user', async () => {
  let definition
  let storedToken = ''
  global.App = app => { definition = app }
  global.wx = {
    cloud: {
      init: options => { global.cloudInit = options },
      callContainer: options => options.success({ statusCode: 200, data: { access_token: 'test-token', user: { id: 'local-admin', role: 'admin' } } })
    },
    login: options => options.success({ code: 'development-code' }),
    setStorageSync: (_key, value) => { storedToken = value },
    showToast: () => {},
    showModal: () => {}
  }

  const appModule = path.resolve(__dirname, '../../miniprogram/app.js')
  delete require.cache[appModule]
  require(appModule)

  let callbackUser = null
  definition.initializeCloud()
  definition.login(user => { callbackUser = user })
  await new Promise(resolve => setImmediate(resolve))

  assert.equal(storedToken, 'test-token')
  assert.deepEqual(callbackUser, { id: 'local-admin', role: 'admin' })
  assert.equal(definition.globalData.environment, 'production')
  assert.deepEqual(global.cloudInit, { env: 'prod-d6gkf5lgbb9d67abc' })
})
