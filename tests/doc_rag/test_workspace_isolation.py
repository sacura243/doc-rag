from doc_rag.vector_store import VectorStore
from doc_rag.config import Config
from doc_rag import rag


def test_query_only_returns_chunks_from_requested_workspace(tmp_path):
    store = VectorStore(str(tmp_path / "chroma"), "workspace-test")
    store.add_chunks(
        ["default workspace document", "other workspace document"],
        [
            {"source": "default.txt", "workspace_id": "default"},
            {"source": "other.txt", "workspace_id": "other"},
        ],
        [[1.0, 0.0], [1.0, 0.0]],
    )

    result = store.query([1.0, 0.0], top_k=2, workspace_id="default")

    assert result["documents"][0] == ["default workspace document"]


def test_deleting_source_only_removes_chunks_in_requested_workspace(tmp_path):
    store = VectorStore(str(tmp_path / "chroma"), "workspace-delete-test")
    store.add_chunks(
        ["default document", "other document"],
        [
            {"source": "shared.txt", "workspace_id": "default"},
            {"source": "shared.txt", "workspace_id": "other"},
        ],
        [[1.0, 0.0], [1.0, 0.0]],
    )

    deleted = store.delete_source("shared.txt", workspace_id="default")

    assert deleted == 1
    assert store.count(workspace_id="default") == 0
    assert store.count(workspace_id="other") == 1


def test_ingestion_tags_each_chunk_with_requested_workspace(monkeypatch, tmp_path):
    captured = {}

    class FakeStore:
        def __init__(self, *_args):
            pass

        def add_chunks(self, _texts, metadatas, _embeddings):
            captured["metadatas"] = metadatas

        def count(self):
            return 1

    monkeypatch.setattr(rag, "VectorStore", FakeStore)
    monkeypatch.setattr(rag, "read_file_sections", lambda _path: [{"text": "document text", "page": None}])
    monkeypatch.setattr(rag, "embed_documents", lambda texts, _cfg: [[1.0] for _ in texts])

    rag.ingest_files(Config(db_dir=str(tmp_path), collection="test"), ["document.txt"], workspace_id="default")

    assert captured["metadatas"] == [{"source": "document.txt", "workspace_id": "default"}]


def test_source_summary_only_lists_requested_workspace(tmp_path):
    store = VectorStore(str(tmp_path / "chroma"), "workspace-summary-test")
    store.add_chunks(
        ["default", "other"],
        [{"source": "default.txt", "workspace_id": "default"}, {"source": "other.txt", "workspace_id": "other"}],
        [[1.0, 0.0], [1.0, 0.0]],
    )

    summary = store.source_summary(workspace_id="default")

    assert [item["source"] for item in summary] == ["default.txt"]
