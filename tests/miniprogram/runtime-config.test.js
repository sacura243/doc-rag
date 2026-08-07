const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

test('runtime config selects the public API and real WeChat login by default', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const config = require(modulePath)

  assert.equal(config.environment, 'production')
  assert.equal(config.apiBaseUrl, '')
  assert.equal(config.loginPath, '/auth/wechat')
  assert.equal(config.transport, 'cloud-container')
  assert.equal(config.cloudEnv, 'prod-d6gkf5lgbb9d67abc')
  assert.equal(config.cloudService, 'knowledge-api')
})

test('production config uses CloudBase transport and real WeChat login', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const { getRuntimeConfig } = require(modulePath)
  const config = getRuntimeConfig('production')

  assert.equal(config.loginPath, '/auth/wechat')
  assert.equal(config.transport, 'cloud-container')
  assert.equal(config.cloudEnv, 'prod-d6gkf5lgbb9d67abc')
})
