# 企业知识库智能助手

一个面向产品、运营、客服等业务团队的本地 RAG 知识库应用。用户可上传产品文档、运营 SOP、客户 FAQ、会议纪要等资料，系统完成本地向量化和检索，再基于引用原文生成回答。

## 功能

- 支持 PDF、DOCX、TXT 多格式资料上传与批量入库
- FastEmbed 本地向量化，Chroma 持久化向量检索
- 讯飞星火大模型基于检索内容生成回答
- 回答展示来源文件、PDF 页码和原文片段，支持溯源
- 已导入资料列表、片段统计、对话记录、知识库清空重建
- 内置产品说明、客服退款 SOP、产品周会纪要三份演示资料

## 技术栈

Python · Streamlit · FastEmbed · Chroma · 讯飞星火 API · pypdf · python-docx

## 快速开始

```powershell
cd D:\Pythonstudy\PythonProject\doc-rag
D:\tools\Python\python.exe -m pip install -r requirements.txt
```

复制 `config.example.toml` 为 `config.toml`，填写讯飞星火 API 配置后，双击 `start_web.bat`，或运行：

```powershell
D:\tools\Python\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

浏览器访问 `http://127.0.0.1:8501`。

## 演示流程

1. 点击“清空并重建知识库”。
2. 点击“导入互联网产品资料样例”。
3. 选择示例问题，例如“退款申请的处理时效和流程是什么？”。
4. 查看回答下方的来源文件与原文片段。

## 项目结构

```text
doc-rag/
├── app.py                  # Streamlit 企业知识库网页
├── main.py                 # 命令行入口
├── doc_rag/
│   ├── readers.py          # 多格式文档解析，PDF 保留页码
│   ├── chunking.py         # 文本分块
│   ├── embeddings.py       # 本地 / 讯飞向量化
│   ├── vector_store.py     # Chroma 存储、资料统计、清空重建
│   └── rag.py              # 入库、检索、溯源问答
└── demo_product_docs/      # 产品、客服、运营演示资料
```

## 说明

- `config.toml`、`chroma_db/`、`models/` 不会上传到 GitHub。
- 本项目默认运行在 `127.0.0.1`，资料和知识库仅保留在本机。

## Streamlit Cloud 在线演示部署

可以部署为公开演示链接，但请不要把密钥写进 GitHub。

1. 在 Streamlit Cloud 选择仓库 `sacura243/doc-rag`、分支 `main`、主文件 `app.py`。
2. 在部署页面的 **Advanced settings -> Secrets** 粘贴 `streamlit_secrets.example.toml` 的内容，并替换为自己的讯飞密钥。
3. 点击 Deploy。

注意：免费演示实例的本地磁盘不是永久存储。服务重启、休眠或重新部署后，上传资料和 Chroma 索引可能被清空；正式产品需要接入云端对象存储和托管数据库。
