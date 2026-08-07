const assert = require('node:assert/strict')
const test = require('node:test')
const path = require('node:path')

test('runtime config selects the public API and real WeChat login by default', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const config = require(modulePath)

  assert.equal(config.environment, 'production')
  assert.equal(config.apiBaseUrl, 'https://knowledge-api-293465-10-1465019784.sh.run.tcloudbase.com/api/v1')
  assert.equal(config.loginPath, '/auth/wechat')
})

test('production config requires an HTTPS API endpoint and real WeChat login', () => {
  const modulePath = path.resolve(__dirname, '../../miniprogram/config.js')
  delete require.cache[modulePath]
  const { getRuntimeConfig } = require(modulePath)
  const config = getRuntimeConfig('production')

  assert.equal(config.loginPath, '/auth/wechat')
  assert.match(config.apiBaseUrl, /^https:\/\//)
})
