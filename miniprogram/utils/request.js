const app = getApp()

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.apiBaseUrl}${options.path}`,
      method: options.method || 'GET',
      data: options.data,
      header: { Authorization: `Bearer ${wx.getStorageSync('accessToken') || ''}` },
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(response.data)
        reject(new Error(response.data && response.data.detail ? response.data.detail : '请求失败'))
      },
      fail() { reject(new Error('无法连接知识库服务')) }
    })
  })
}

module.exports = { request }
