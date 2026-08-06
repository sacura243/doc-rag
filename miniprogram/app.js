const runtimeConfig = require('./config')

App({
  globalData: { apiBaseUrl: runtimeConfig.apiBaseUrl, user: null },
  onLaunch() { this.login() },
  login() {
    if (!this.globalData.apiBaseUrl) {
      return wx.showModal({ title: '服务地址未配置', content: '请先在 config.js 中配置正式 HTTPS API 地址。', showCancel: false })
    }
    wx.login({
      success: ({ code }) => wx.request({
        url: `${this.globalData.apiBaseUrl}${runtimeConfig.loginPath}`, method: 'POST', data: { code },
        success: ({ statusCode, data }) => {
          if (statusCode === 200) {
            wx.setStorageSync('accessToken', data.access_token)
            this.globalData.user = data.user
            return
          }
          wx.showToast({ title: '登录知识库失败', icon: 'none' })
        },
        fail: () => wx.showToast({ title: '无法连接知识库服务', icon: 'none' })
      }),
      fail: () => wx.showToast({ title: '微信登录失败', icon: 'none' })
    })
  }
})
