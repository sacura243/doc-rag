# 发现记录

## 2026-08-07

- 后端已有健康检查、开发登录、资料上传/删除/重建和问答接口。
- 前端问答页只显示回答，尚未显示 `sources`。
- 前端资料页缺少上传进度、大小/格式预校验、重建入口和稳定的错误提示。
- API 已覆盖登录、基础问答、上传、删除和成员读取；尚未覆盖重建及成员写操作被拒绝。
- 小程序本地 API 地址为 `http://127.0.0.1:8010/api/v1`；真机不能直接访问该地址，后续需要 LAN 地址或 HTTPS 域名。
- 本轮完成后，发布阻塞仅剩用户侧的 HTTPS 域名、微信真实登录密钥配置、备案/审核与真机验证；本地开发流程不受影响。

## GitHub 参考调研（2026-08-07）

| 项目 | 用途 | 维护/规模 | 许可与风险 | 适配判断 |
|---|---|---:|---|---|
| [wechat-miniprogram/weui-miniprogram](https://github.com/wechat-miniprogram/weui-miniprogram) | 微信小程序组件库，适合按钮、表单、上传、进度、空状态 | 约 2.4k stars，2026-04 更新 | MIT，适合直接引入；仍需保留版权声明 | 最适合当前小程序，适配成本低 |
| [Tencent/weui-wxss](https://github.com/Tencent/weui-wxss) | 微信官方视觉基础样式 | 约 15k stars，2026-03 更新 | 仓库标注 MIT/WeUI 许可，使用前保留许可文件 | 可借鉴视觉规范，组件逻辑仍需自己接 |
| [labring/FastGPT](https://github.com/labring/FastGPT) | 成熟知识库/问答工作台，适合参考资料列表、引用和管理端布局 | 约 29k stars，持续更新 | FastGPT Open Source License，不允许未经授权提供 SaaS；不直接复制代码 | 适合借鉴信息层级，直接移植成本高 |
| [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | 企业级 RAG 产品，适合参考文档处理、检索结果和引用展示 | 约 87k stars，持续更新 | Apache-2.0，需保留许可和 NOTICE | Web 架构重，适合视觉参考，不适合直接移植小程序 |
| [1Panel-dev/MaxKB](https://github.com/1Panel-dev/MaxKB) | 企业级智能体/知识库后台 | 约 22k stars，持续更新 | GPL-3.0，若复制/分发衍生代码会带来开源义务 | 只参考流程，不直接复制实现 |
| [langgenius/dify](https://github.com/langgenius/dify) | 工作区、知识库和对话产品的成熟交互参考 | 约 151k stars，持续更新 | Dify 自定义许可，不能按 MIT/Apache 直接使用 | 参考布局与信息架构，避免代码移植 |

结论：下一版界面采用“知答库工作台”方向，并优先接入 MIT 的 `weui-miniprogram` 组件或按其视觉规范重写现有原生页面；FastGPT/RAGFlow/Dify 只借鉴信息架构和引用展示方式，不直接复制受限代码。
