App({
  globalData: { apiBaseUrl: 'http://127.0.0.1:8010/api/v1', user: null },
  onLaunch() { this.login() },
  login() {
    wx.login({
      success: ({ code }) => wx.request({
        url: `${this.globalData.apiBaseUrl}/auth/wechat`, method: 'POST', data: { code },
        success: ({ statusCode, data }) => {
          if (statusCode === 200) { wx.setStorageSync('accessToken', data.access_token); this.globalData.user = data.user }
        }
      })
    })
  }
})
