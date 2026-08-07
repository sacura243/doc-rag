# 生产发布清单

## 服务器与 HTTPS

- [ ] 准备 Linux 云服务器，开放 TCP 80、443。
- [ ] 为 API 准备独立域名，例如 `api.example.com`，DNS A 记录指向服务器。
- [ ] 在服务器执行 `docker compose -f deploy/docker-compose.yml up -d --build`。
- [ ] 验证 `https://<域名>/api/v1/health` 返回 `{"status":"ok"}`。
- [ ] 确认上传目录、Chroma 数据、模型缓存和 SQLite 数据均为持久化存储。

## 微信公众平台

- [ ] 小程序主体完成实名认证；需要备案时，完成 ICP 备案和公安备案要求。
- [ ] 若使用自定义域名，在“开发管理 > 开发设置 > 服务器域名”配置 request/uploadFile 合法域名；若使用 CloudBase SDK，则无需把云托管测试域名加入服务器域名。
- [ ] 服务器环境设置 `API_ENV=production`、`API_JWT_SECRET`、`WECHAT_APPID`、`WECHAT_APPSECRET` 和管理员 OpenID。
- [ ] `miniprogram/config.js` 的 `ENVIRONMENT` 改为 `production`，并确认 `transport`、CloudBase 环境 ID 和服务名正确。
- [ ] 执行 `node scripts/check_release.js`，通过后再上传体验版。

## 审核说明建议

功能描述：企业内部知识库问答工具，管理员上传 TXT、PDF、DOCX 制度资料，成员通过自然语言查询并查看引用来源。

隐私说明：仅使用微信登录凭证换取用户标识，用于账号识别和权限控制；上传的企业资料只用于本小程序知识库检索，不公开展示。

审核测试路径：微信登录 -> 管理员上传测试资料 -> 首页提问“报销需要哪些材料？” -> 查看回答和引用来源 -> 资料管理页删除或重建索引。

## 真机验收

- [ ] 管理员登录后可上传 1 个 TXT、PDF、DOCX，进度和错误提示正常。
- [ ] 普通成员只能问答和查看资料，不能上传、删除或重建索引。
- [ ] 空问题、超长问题、超大文件和不支持格式均有明确提示。
- [ ] 断网、API 502、登录失效时能看到可恢复的错误提示。
- [ ] 在 iPhone 和 Android 各检查首页、资料页的长标题、键盘弹出、滚动和安全区域。
