# 知答库小程序本地联调

## 当前已完成的流程

- 本地开发登录：启动后自动获得管理员权限，仅限 `API_ENV=development`。
- 首页工作台：首屏提供问答、上传资料、资料管理、资料统计和最近资料入口。
- 资料管理：上传 TXT、PDF、DOCX；单文件最大 10 MB；一次最多 5 个文件；可删除和重建索引。
- 问答：回答下方展示资料名、页码和检索到的证据片段。
- 后端按 `default` 工作区重建索引，不会清空其他工作区的数据。

## 启动后端

在 PowerShell 运行：

```powershell
cd D:\Pythonstudy\PythonProject\doc-rag-wechat
powershell -ExecutionPolicy Bypass -File .\scripts\start_api.ps1
```

浏览器打开 `http://127.0.0.1:8010/api/v1/health`。显示 `{"status":"ok"}` 即表示服务已启动。

若问答或导入提示模型服务不可用，将原项目中本机私有的 `config.toml` 复制到当前工作树根目录。该文件含密钥，不能提交 Git 或发送到聊天：

```powershell
Copy-Item D:\Pythonstudy\PythonProject\doc-rag\config.toml .\config.toml
```

## 微信开发者工具

1. 打开项目目录 `D:\Pythonstudy\PythonProject\doc-rag-wechat\miniprogram`。
2. 在“详情” > “本地设置”中开启“不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书”。这项只可用于本地开发。
3. 点击“编译”。
4. 在“资料”页上传一个 TXT、PDF 或 DOCX 文件，等待进度完成。
5. 回到“问答”页提出与资料有关的问题，确认回答下方显示“参考资料”。
6. 在“资料”页点击“重建索引”，确认资料列表仍可正常显示。

首页管理员应能直接看到“上传资料”和“资料管理”两个快捷入口；成员只看到资料管理入口。

## 正式发布前

`miniprogram/config.js` 当前为开发模式。正式发布时：

1. 将 `ENVIRONMENT` 改为 `production`。
2. 在 `production.apiBaseUrl` 填入已备案的 HTTPS API 域名。
3. 在微信公众平台配置 request 合法域名。
4. 后端设置 `WECHAT_APPID`、`WECHAT_APPSECRET`、`API_JWT_SECRET` 和 `WECHAT_ADMIN_OPENIDS`。不要提交或发送这些值。
5. 使用 `/auth/wechat` 完成真实微信登录，并完成微信审核、备案和发布流程。

真机无法访问 `127.0.0.1`。真机预览前需要部署 HTTPS API，或在同一局域网下改为电脑的局域网 IP 进行临时调试。
