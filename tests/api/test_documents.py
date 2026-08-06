import asyncio

import httpx

from api.main import create_app
from api.services.auth import create_access_token
from api.services.users import User


def test_administrator_can_upload_supported_document(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")

    from api.routers import documents

    monkeypatch.setattr(documents, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())
    monkeypatch.setattr(documents, "ingest_files", lambda *_args, **_kwargs: {"files": 1, "chunks": 2, "total_chunks": 2})
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    async def upload() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=[("files", ("guide.txt", b"knowledge base content", "text/plain"))],
            )

    response = asyncio.run(upload())

    assert response.status_code == 201
    assert response.json() == {"files": 1, "chunks": 2, "total_chunks": 2}
    assert len(list((tmp_path / "uploads").glob("*.txt"))) == 1


def test_administrator_can_list_and_delete_document(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    stored = upload_dir / "abc123_guide.txt"
    stored.write_text("content", encoding="utf-8")
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    from api.routers import documents
    monkeypatch.setattr(documents, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())

    class FakeStore:
        def __init__(self, *_args):
            pass

        def source_summary(self, workspace_id=None):
            return [{"source": str(stored), "chunks": 2, "pages": set()}]

        def delete_source(self, source, workspace_id=None):
            assert source == str(stored)
            return 2

    monkeypatch.setattr(documents, "VectorStore", FakeStore)

    async def request() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {token}"}
            listing = await client.get("/api/v1/documents", headers=headers)
            deletion = await client.delete("/api/v1/documents/abc123_guide.txt", headers=headers)
            return listing, deletion

    listing, deletion = asyncio.run(request())

    assert listing.status_code == 200
    assert listing.json()["items"] == [{"id": "abc123_guide.txt", "name": "guide.txt", "chunks": 2}]
    assert deletion.status_code == 200
    assert deletion.json() == {"deleted_chunks": 2}
    assert not stored.exists()


def test_member_can_read_document_list(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    from api.routers import documents
    monkeypatch.setattr(documents, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())
    class FakeStore:
        def __init__(self, *_args): pass
        def source_summary(self, workspace_id=None): return []
    monkeypatch.setattr(documents, "VectorStore", FakeStore)
    token = create_access_token(User(id="member-id", openid="member", role="member"), "test-signing-secret-with-32-bytes")
    async def listing():
        transport=httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport,base_url="http://test") as client:
            return await client.get('/api/v1/documents',headers={'Authorization':f'Bearer {token}'})
    assert asyncio.run(listing()).status_code == 200


def test_administrator_rebuild_clears_only_default_workspace(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    (upload_dir / "guide.txt").write_text("knowledge base content", encoding="utf-8")
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")

    from api.routers import documents

    monkeypatch.setattr(documents, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())
    monkeypatch.setattr(
        documents,
        "ingest_files",
        lambda *_args, **_kwargs: {"files": 1, "chunks": 2, "total_chunks": 2},
    )

    class FakeStore:
        deleted_workspace = None

        def __init__(self, *_args):
            pass

        def reset(self):
            raise AssertionError("rebuild must not reset every workspace")

        def delete_workspace(self, workspace_id):
            FakeStore.deleted_workspace = workspace_id

    monkeypatch.setattr(documents, "VectorStore", FakeStore)
    token = create_access_token(
        User(id="admin-id", openid="admin", role="admin"),
        "test-signing-secret-with-32-bytes",
    )

    async def rebuild() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/rebuild",
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(rebuild())

    assert response.status_code == 200
    assert response.json() == {"files": 1, "chunks": 2, "total_chunks": 2}
    assert FakeStore.deleted_workspace == "default"
