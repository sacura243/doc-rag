const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

test('runtime config selects local API and development login by default', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const config = require(modulePath)

  assert.equal(config.environment, 'development')
  assert.equal(config.apiBaseUrl, 'http://127.0.0.1:8010/api/v1')
  assert.equal(config.loginPath, '/auth/development')
})

test('production config requires an HTTPS API endpoint and real WeChat login', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const { getRuntimeConfig } = require(modulePath)
  const config = getRuntimeConfig('production')

  assert.equal(config.loginPath, '/auth/wechat')
  assert.equal(config.apiBaseUrl, '')
})
