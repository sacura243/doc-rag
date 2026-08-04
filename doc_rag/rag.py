"""RAG 检索增强问答。"""
from .config import Config
from .embeddings import embed_documents, embed_query
from .llm import SparkChat
from .readers import iter_docs, read_file
from .chunking import split_text
from .vector_store import VectorStore


def ingest_folder(cfg: Config, folder: str) -> int:
    store = VectorStore(cfg.db_dir, cfg.collection)
    texts, metadatas = [], []
    total_files = 0
    for path in iter_docs(folder):
        content = read_file(path)
        if not content.strip():
            print(f"跳过空文件: {path}")
            continue
        chunks = split_text(content, cfg.chunk_size, cfg.chunk_overlap)
        for c in chunks:
            texts.append(c)
            metadatas.append({"source": path})
        total_files += 1
        print(f"已解析 {path} -> {len(chunks)} 块")
    if texts:
        print(f"正在向量化 {len(texts)} 个文本块 ...")
        embeddings = embed_documents(texts, cfg)
        store.add_chunks(texts, metadatas, embeddings)
        print(f"入库完成，共 {store.count()} 个片段")
    return total_files


def ask_with_sources(cfg: Config, question: str, top_k: int = 4) -> tuple[str, list[dict]]:
    """回答问题，并返回用于生成回答的检索片段。"""
    store = VectorStore(cfg.db_dir, cfg.collection)
    chunk_count = store.count()
    if chunk_count == 0:
        return "知识库为空，请先导入文档。", []
    q_emb = embed_query(question, cfg)
    result = store.query(q_emb, min(top_k, chunk_count))
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    sources = [
        {"source": metas[i].get("source", "未知来源"), "content": doc}
        for i, doc in enumerate(docs)
    ]
    context = "\n\n".join(
        f"[来源 {metas[i].get('source', '?')}]\n{doc}" for i, doc in enumerate(docs)
    )
    prompt = (
        "请只根据下面的资料回答问题；如果资料里没有答案，请直接说明“资料中未找到”。\n\n"
        f"资料：\n{context}\n\n问题：{question}\n回答："
    )
    return SparkChat(cfg).chat(prompt), sources


def ask(cfg: Config, question: str, top_k: int = 4) -> str:
    """兼容原有命令行调用，只返回回答文本。"""
    answer, _sources = ask_with_sources(cfg, question, top_k)
    return answer
