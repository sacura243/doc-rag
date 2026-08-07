const assert = require('node:assert/strict')
const { getRuntimeConfig } = require('../miniprogram/config')

const config = getRuntimeConfig('production')
assert.equal(config.loginPath, '/auth/wechat', 'production must use real WeChat login')
if (config.transport === 'cloud-container') {
  assert.match(config.cloudEnv, /^[a-z][a-z0-9-]+$/, 'CloudBase environment ID is required')
  assert.match(config.cloudService, /^[a-z][a-z0-9-]+$/, 'CloudBase service name is required')
} else {
  assert.match(config.apiBaseUrl, /^https:\/\/[^/]+\/api\/v1$/, 'production API must be an HTTPS domain ending in /api/v1')
}

console.log(`release configuration looks valid for ${config.transport || 'http'}`)
