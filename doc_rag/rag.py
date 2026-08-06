"""Document ingestion and retrieval-augmented generation workflows."""
from __future__ import annotations

from .chunking import split_text
from .config import Config
from .embeddings import embed_documents, embed_query
from .llm import SparkChat
from .readers import iter_docs, read_file_sections
from .vector_store import VectorStore


def ingest_files(cfg: Config, file_paths: list[str], workspace_id: str = "default") -> dict:
    store = VectorStore(cfg.db_dir, cfg.collection)
    texts, metadatas, imported_files = [], [], []

    for path in file_paths:
        sections = read_file_sections(path)
        file_chunks = 0
        for section in sections:
            content = section["text"]
            if not content.strip():
                continue
            for chunk in split_text(content, cfg.chunk_size, cfg.chunk_overlap):
                metadata = {"source": path, "workspace_id": workspace_id}
                if section["page"] is not None:
                    metadata["page"] = section["page"]
                texts.append(chunk)
                metadatas.append(metadata)
                file_chunks += 1
        if file_chunks:
            imported_files.append(path)

    if texts:
        embeddings = embed_documents(texts, cfg)
        store.add_chunks(texts, metadatas, embeddings)
    return {"files": len(imported_files), "chunks": len(texts), "total_chunks": store.count()}


def ingest_folder(cfg: Config, folder: str) -> int:
    result = ingest_files(cfg, list(iter_docs(folder)))
    return result["files"]


def retrieve_sources(cfg: Config, question: str, top_k: int = 4, workspace_id: str = "default") -> list[dict]:
    """Retrieve source chunks without calling the LLM; used by the evaluation page."""
    store = VectorStore(cfg.db_dir, cfg.collection)
    chunk_count = store.count(workspace_id=workspace_id)
    if chunk_count == 0:
        return []
    result = store.query(embed_query(question, cfg), min(top_k, chunk_count), workspace_id=workspace_id)
    return [
        {
            "source": result["metadatas"][0][index].get("source", "unknown"),
            "content": document,
            "page": result["metadatas"][0][index].get("page"),
        }
        for index, document in enumerate(result["documents"][0])
    ]


def ask_with_sources(cfg: Config, question: str, top_k: int = 4, workspace_id: str = "default") -> tuple[str, list[dict]]:
    store = VectorStore(cfg.db_dir, cfg.collection)
    chunk_count = store.count(workspace_id=workspace_id)
    if chunk_count == 0:
        return "\u77e5\u8bc6\u5e93\u4e3a\u7a7a\uff0c\u8bf7\u5148\u5bfc\u5165\u6587\u6863\u3002", []

    sources = retrieve_sources(cfg, question, top_k, workspace_id=workspace_id)

    context = "\n\n".join(
        f"[\u6765\u6e90: {item['source']}{' | \u7b2c' + str(item['page']) + '\u9875' if item['page'] else ''}]\n{item['content']}"
        for item in sources
    )
    prompt = (
        "\u4f60\u662f\u4f01\u4e1a\u77e5\u8bc6\u5e93\u52a9\u624b\u3002\u53ea\u80fd\u6839\u636e\u4e0b\u65b9\u7ed9\u51fa\u7684\u8d44\u6599\u56de\u7b54\u95ee\u9898\u3002"
        "\u5982\u679c\u8d44\u6599\u4e2d\u6ca1\u6709\u660e\u786e\u4fe1\u606f\uff0c\u8bf7\u76f4\u63a5\u8bf4\u201c\u8d44\u6599\u4e2d\u672a\u627e\u5230\u4f9d\u636e\u201d\uff0c"
        "\u4e0d\u8981\u8865\u5145\u63a8\u6d4b\u3002\u56de\u7b54\u7b80\u6d01\uff0c\u5fc5\u8981\u65f6\u5206\u70b9\u3002\n\n"
        f"\u8d44\u6599\uff1a\n{context}\n\n\u95ee\u9898\uff1a{question}\n\u56de\u7b54\uff1a"
    )
    return SparkChat(cfg).chat(prompt), sources


def ask(cfg: Config, question: str, top_k: int = 4) -> str:
    answer, _sources = ask_with_sources(cfg, question, top_k)
    return answer
