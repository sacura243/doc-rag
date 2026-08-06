# 进度日志

## 2026-08-07

- 恢复 `feature/wechat-mini-program` 工作树并确认基础提交已存在。
- 开始核对小程序页面、API 路由与现有测试，准备按测试先行补齐剩余用户流程。
- 修复资料重建会清空全量 Chroma collection 的问题，改为只删除 `default` 工作区，并新增回归测试。
- 问答页新增来源展示；资料页新增格式/大小预校验、上传进度、失败提示和重建索引入口。
- 新增开发/生产运行配置模块；默认仍走本机 API 和开发登录。
- 验证：`pytest tests/api -q` 通过 13 项；`node --test tests/miniprogram/*.test.js` 通过 5 项；健康检查返回 `{"status":"ok"}`。
