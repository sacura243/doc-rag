"""Persistent Chroma storage used by the RAG application."""
from __future__ import annotations

import uuid

import chromadb


class VectorStore:
    def __init__(self, db_dir: str, collection: str):
        self.db_dir = db_dir
        self.collection_name = collection
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, texts: list[str], metadatas: list[dict], embeddings: list[list]) -> None:
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, embedding: list, top_k: int = 4) -> dict:
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)

    def count(self) -> int:
        return self.collection.count()

    def source_summary(self) -> list[dict]:
        """Return one record per imported source with its chunk count."""
        data = self.collection.get(include=["metadatas"])
        grouped: dict[tuple[str, int | None], int] = {}
        for metadata in data.get("metadatas", []):
            source = metadata.get("source", "unknown")
            page = metadata.get("page")
            key = (source, page if isinstance(page, int) else None)
            grouped[key] = grouped.get(key, 0) + 1

        by_source: dict[str, dict] = {}
        for (source, page), chunks in grouped.items():
            item = by_source.setdefault(source, {"source": source, "chunks": 0, "pages": set()})
            item["chunks"] += chunks
            if page:
                item["pages"].add(page)
        return sorted(by_source.values(), key=lambda item: item["source"].lower())

    def reset(self) -> None:
        """Clear all chunks while keeping the same collection name."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )
