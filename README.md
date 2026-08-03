# 文档智能处理与 RAG 问答系统（doc-rag）

基于 **Python + 讯飞星火大模型 API + 本地向量化 + Chroma 向量库** 的轻量级知识库问答工具，两个核心能力：

1. **批量总结**：遍历文件夹里的 txt / pdf / docx，自动提炼核心要点并导出。
2. **RAG 问答**：文档分块 → 本地 Embedding 向量化 → 存入 Chroma → 用自然语言提问，基于自有资料回答。

## 亮点

- 🆓 **向量化零成本**：默认使用本地 `bge-small-zh-v1.5` 模型（免费、离线、中文效果好、无需申请任何授权），模型首次运行自动下载到 `models/` 目录。
- 🔄 **可切换讯飞 Embedding**：在 `config.toml` 把 `embed_backend` 改为 `"xfyun"` 即可切回讯飞文本向量化（需在讯飞平台单独申请授权；注意两种后端向量维度不同，切换后需清空 `chroma_db` 重新入库）。
- 🧩 **兼容文本框简历**：docx 读取同时解析段落、表格和文本框/画布中的文字，能正确处理市面上大部分简历模板。

## 快速开始

### 1. 安装依赖（Windows，用清华镜像更快）

```powershell
cd D:\Pythonstudy\PythonProject\doc-rag
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 本地向量化依赖 `fastembed` / `onnxruntime`；若只使用讯飞方案可省略。

### 2. 配置密钥（二选一）

方式 A（推荐，环境变量）：
```powershell
setx XF_APPID "你的APPID"
setx XF_APIKEY "你的APIKey"
setx XF_APISECRET "你的APISecret"
```
设置后**重开终端**生效。

方式 B（配置文件）：
复制 `config.example.toml` 为 `config.toml` 并填入密钥。

> 需要讯飞开放平台开通「星火大模型」对话服务；向量化默认走本地模型，无需讯飞授权。

### 3. 使用

```powershell
# 批量总结
python main.py summarize --input E:\资料 --output E:\总结

# 文档入库（分块 + 本地向量化）
python main.py ingest --dir E:\资料

# 基于知识库问答
python main.py ask "这份文档的核心结论是什么？"
python main.py ask "退货流程怎么走？" --top-k 5
```

## 项目结构

```
doc-rag/
├── main.py                 # 命令行入口（summarize / ingest / ask）
├── doc_rag/
│   ├── config.py           # 配置加载（环境变量 / config.toml，含向量化后端开关）
│   ├── readers.py          # 文档读取：txt / pdf / docx（含文本框）
│   ├── chunking.py         # 文本分块（按句切分 + 重叠）
│   ├── embeddings.py       # 向量化：本地 bge（默认） / 讯飞 Embedding（可切换）
│   ├── vector_store.py     # Chroma 向量库封装
│   ├── llm.py              # 讯飞星火对话（WebSocket）
│   └── rag.py              # RAG 检索 + 生成
├── models/                 # 本地向量模型缓存（自动下载）
├── requirements.txt
└── config.example.toml
```

## 技术要点（面试可讲）

- **分块策略**：按句子切分 + 重叠窗口，避免把一句话拦腰切断导致语义断裂
- **向量化**：默认本地 `bge-small-zh-v1.5`（512 维，ONNX 推理，CPU 即可跑），也可切换讯飞 Embedding（2560 维）
- **检索**：Chroma 余弦相似度检索 top-k，返回最相关的文档片段
- **生成**：把检索片段拼进提示词，让大模型"只根据资料回答"，缓解幻觉
- **可扩展**：检索结果可继续做重排（rerank）、带来源引用等

## 待办（可选）

- [ ] 重排（rerank）提升检索精度
- [ ] Streamlit 网页版
- [ ] FastAPI 接口封装