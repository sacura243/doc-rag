const app = getApp()

function request(options) {
  return new Promise((resolve, reject) => {
    const call = {
      method: options.method || 'GET',
      data: options.data,
      header: { Authorization: `Bearer ${wx.getStorageSync('accessToken') || ''}` },
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(response.data)
        reject(new Error(response.data && response.data.detail ? response.data.detail : '请求失败'))
      },
      fail() { reject(new Error('无法连接知识库服务')) }
    }
    if (app.globalData.transport === 'cloud-container') {
      call.config = { env: app.globalData.cloudEnv }
      call.service = app.globalData.cloudService
      call.path = `/api/v1${options.path}`
      return wx.cloud.callContainer(call)
    }
    call.url = `${app.globalData.apiBaseUrl}${options.path}`
    return wx.request(call)
  })
}

module.exports = { request }
