"""Chroma 向量库封装。"""
import uuid

import chromadb


class VectorStore:
    def __init__(self, db_dir: str, collection: str):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, texts: list, metadatas: list, embeddings: list):
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, embedding: list, top_k: int = 4):
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)

    def count(self) -> int:
        return self.collection.count()