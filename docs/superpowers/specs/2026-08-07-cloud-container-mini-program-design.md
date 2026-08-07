# 云容器免域名小程序调用设计

## 目标

在不购买自有域名的前提下，让微信小程序通过微信云开发能力访问当前 FastAPI 云托管服务，保留真实微信登录、问答、资料管理和管理员权限。

## 现状与约束

- 云托管环境 ID：`prod-d6gkf5lgbb9d67abc`
- 云托管服务名：`knowledge-api`
- 后端已有 REST 路径前缀：`/api/v1`
- 当前小程序使用 `wx.request` 和 `wx.uploadFile` 访问公网 URL。
- 云托管生成的 `*.sh.run.tcloudbase.com` 域名只适合测试，不能作为正式服务器域名配置。

## 方案

### JSON 接口

小程序请求封装增加 `cloudContainer` 传输模式，使用 `wx.cloud.callContainer`，固定环境 ID 和服务名，并保留现有 `/api/v1` 路径。登录、问答、资料列表、删除和重建索引全部复用现有 REST 路径和 Bearer token。

### 文件上传

文件先使用 `wx.cloud.uploadFile` 上传到云存储，再使用 `wx.cloud.getTempFileURL` 换取短期 HTTPS 下载地址。小程序调用后端新增的管理员导入接口，提交临时地址、原始文件名和 MIME 类型。后端以超时和最大响应大小下载文件到 `API_UPLOAD_DIR`，复用现有文件校验和 `ingest_files` 流程。导入完成后小程序删除云存储临时对象，避免存储泄漏。

### 配置

小程序生产配置使用：

- `transport: 'cloud-container'`
- `cloudEnv: 'prod-d6gkf5lgbb9d67abc'`
- `cloudService: 'knowledge-api'`
- `loginPath: '/auth/wechat'`

开发配置继续保留局域网 HTTP 模式，方便离线开发。

## 错误处理与权限

- 云容器调用失败沿用现有网络错误提示，并区分登录失败、服务不可用和权限不足。
- 云存储上传失败不调用后端导入接口。
- 后端导入接口只允许管理员 Bearer token，并限制扩展名、大小和路径名。
- 导入失败删除已下载的临时文件和云存储对象。
- 后端只接受 HTTPS 临时地址，限制响应大小和下载超时，并拒绝本地/内网地址，降低 SSRF 风险。

## 验证

- 单元测试覆盖云容器请求配置、上传导入成功、格式/大小拒绝、权限拒绝和清理失败路径。
- 现有 API 和小程序测试全部保持通过。
- 真机验收覆盖真实微信登录、管理员上传、成员问答、成员禁止上传、断网和服务错误。
