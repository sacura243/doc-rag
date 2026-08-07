const assert = require('node:assert/strict')
const { getRuntimeConfig } = require('../miniprogram/config')

const config = getRuntimeConfig('production')
assert.equal(config.loginPath, '/auth/wechat', 'production must use real WeChat login')
assert.match(config.apiBaseUrl, /^https:\/\/[^/]+\/api\/v1$/, 'production API must be an HTTPS domain ending in /api/v1')

console.log(`release configuration looks valid for ${config.apiBaseUrl}`)
