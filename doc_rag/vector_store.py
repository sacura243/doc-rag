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

    def query(self, embedding: list, top_k: int = 4, workspace_id: str | None = None) -> dict:
        query_args = {"query_embeddings": [embedding], "n_results": top_k}
        if workspace_id is not None:
            query_args["where"] = {"workspace_id": workspace_id}
        return self.collection.query(**query_args)

    def count(self, workspace_id: str | None = None) -> int:
        if workspace_id is None:
            return self.collection.count()
        return len(self.collection.get(where={"workspace_id": workspace_id}, include=[]).get("ids", []))

    def source_summary(self, workspace_id: str | None = None) -> list[dict]:
        """Return one record per imported source with its chunk count."""
        get_args = {"include": ["metadatas"]}
        if workspace_id is not None:
            get_args["where"] = {"workspace_id": workspace_id}
        data = self.collection.get(**get_args)
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

    def delete_workspace(self, workspace_id: str) -> int:
        """Delete chunks belonging to one workspace without affecting others."""
        records = self.collection.get(where={"workspace_id": workspace_id}, include=[])
        ids = records.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def delete_source(self, source: str, workspace_id: str | None = None) -> int:
        """Delete every indexed chunk originating from one source file."""
        where = {"source": source}
        if workspace_id is not None:
            where = {"$and": [{"source": source}, {"workspace_id": workspace_id}]}
        records = self.collection.get(where=where, include=[])
        ids = records.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)
