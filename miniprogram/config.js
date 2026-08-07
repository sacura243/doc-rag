const ENVIRONMENT = 'development'

const environments = {
  development: {
    // 当前电脑的局域网地址，供微信开发者工具/真机访问；换网络后改成电脑新 IP。
    apiBaseUrl: 'http://192.168.1.155:8010/api/v1',
    loginPath: '/auth/development'
  },
  production: {
    // 发布前填写已备案并已在微信公众平台配置的 HTTPS API 域名。
    apiBaseUrl: '',
    loginPath: '/auth/wechat'
  }
}

function getRuntimeConfig(environment) {
  const config = environments[environment]
  if (!config) throw new Error(`Unknown mini program environment: ${environment}`)
  return { environment, ...config }
}

module.exports = { ...getRuntimeConfig(ENVIRONMENT), getRuntimeConfig }
