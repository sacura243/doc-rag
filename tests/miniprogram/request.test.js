const assert = require('node:assert/strict')
const test = require('node:test')

test('request uses CloudBase container in production', async () => {
  const calls = []
  global.getApp = () => ({
    globalData: {
      transport: 'cloud-container',
      cloudEnv: 'prod-d6gkf5lgbb9d67abc',
      cloudService: 'knowledge-api'
    }
  })
  global.wx = {
    getStorageSync: () => 'test-token',
    cloud: {
      callContainer: options => {
        calls.push(options)
        options.success({ statusCode: 200, data: { items: [] } })
      }
    }
  }

  const modulePath = require.resolve('../../miniprogram/utils/request')
  delete require.cache[modulePath]
  const { request } = require(modulePath)
  const data = await request({ path: '/documents', method: 'GET' })

  assert.deepEqual(data, { items: [] })
  assert.equal(calls[0].config.env, 'prod-d6gkf5lgbb9d67abc')
  assert.equal(calls[0].service, 'knowledge-api')
  assert.equal(calls[0].path, '/api/v1/documents')
  assert.equal(calls[0].header.Authorization, 'Bearer test-token')
})
