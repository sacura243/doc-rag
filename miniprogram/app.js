const runtimeConfig = require('./config')

function callApi(options) {
  if (runtimeConfig.transport === 'cloud-container') {
    return wx.cloud.callContainer({
      ...options,
      config: { env: runtimeConfig.cloudEnv },
      service: runtimeConfig.cloudService,
      path: `/api/v1${options.path}`
    })
  }
  return wx.request({ ...options, url: `${runtimeConfig.apiBaseUrl}${options.path}` })
}

App({
  globalData: {
    apiBaseUrl: runtimeConfig.apiBaseUrl,
    environment: runtimeConfig.environment,
    transport: runtimeConfig.transport,
    cloudEnv: runtimeConfig.cloudEnv,
    cloudService: runtimeConfig.cloudService,
    user: null
  },
  initializeCloud() {
    if (runtimeConfig.transport === 'cloud-container' && wx.cloud && runtimeConfig.cloudEnv) {
      wx.cloud.init({ env: runtimeConfig.cloudEnv })
    }
  },
  onLaunch() { this.initializeCloud(); this.login() },
  login(onComplete) {
    const finish = user => { if (typeof onComplete === 'function') onComplete(user) }
    if (runtimeConfig.transport === 'http' && !this.globalData.apiBaseUrl) {
      wx.showModal({ title: '服务地址未配置', content: '请先在 config.js 中配置正式 HTTPS API 地址。', showCancel: false })
      return finish(null)
    }
    wx.login({
      success: ({ code }) => callApi({
        path: runtimeConfig.loginPath, method: 'POST', data: { code },
        success: ({ statusCode, data }) => {
          if (statusCode === 200) {
            wx.setStorageSync('accessToken', data.access_token)
            this.globalData.user = data.user
            return finish(data.user)
          }
          wx.showToast({ title: '登录知识库失败', icon: 'none' })
          finish(null)
        },
        fail: () => { wx.showToast({ title: '无法连接知识库服务', icon: 'none' }); finish(null) }
      }),
      fail: () => { wx.showToast({ title: '微信登录失败', icon: 'none' }); finish(null) }
    })
  }
})
