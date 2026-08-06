# 知答库小程序本地联调

1. 在 PowerShell 运行 `powershell -ExecutionPolicy Bypass -File .\scripts\start_api.ps1`。
2. 确认浏览器访问 `http://127.0.0.1:8010/api/v1/health` 返回 `{"status":"ok"}`。
3. 在微信开发者工具中打开 `miniprogram` 目录。
4. 开发阶段可在开发者工具中关闭“校验合法域名”；正式发布前必须改为已备案 HTTPS 域名。

真实微信登录需在本机环境变量中配置 `WECHAT_APPID`、`WECHAT_APPSECRET`、`API_JWT_SECRET` 和 `WECHAT_ADMIN_OPENIDS`，不要将这些信息提交到 Git 或发送到聊天。
