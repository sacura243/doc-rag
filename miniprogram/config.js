const ENVIRONMENT = 'development'

const environments = {
  development: {
    apiBaseUrl: 'http://127.0.0.1:8010/api/v1',
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
