import asyncio

import httpx

from api.main import create_app
from api.services.auth import create_access_token
from api.services.users import User


class _DownloadResponse:
    status_code = 200
    headers = {"content-length": "21"}

    def raise_for_status(self):
        return None

    def iter_bytes(self, chunk_size=65536):
        yield b"knowledge base content"


class _DownloadClient:
    last_kwargs = {}

    def __init__(self, *_args, **_kwargs):
        _DownloadClient.last_kwargs = _kwargs

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def stream(self, *_args, **_kwargs):
        class _Context:
            def __enter__(self):
                return _DownloadResponse()

            def __exit__(self, *_args):
                return False

        return _Context()


class _LargeDownloadClient(_DownloadClient):
    def stream(self, *_args, **_kwargs):
        class _Context:
            def __enter__(self):
                response = _DownloadResponse()
                response.headers = {"content-length": str(11 * 1024 * 1024)}
                return response

            def __exit__(self, *_args):
                return False

        return _Context()


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


def test_administrator_can_import_document_from_cloud_storage_url(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    monkeypatch.setenv("WECHAT_VERIFY_TLS", "false")

    from api.services import files
    from api.routers import documents

    monkeypatch.setattr(files.httpx, "Client", _DownloadClient)
    monkeypatch.setattr(documents, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())
    monkeypatch.setattr(documents, "ingest_files", lambda *_args, **_kwargs: {"files": 1, "chunks": 2, "total_chunks": 2})
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    async def import_document() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/import-url",
                headers={"Authorization": f"Bearer {token}"},
                json={"url": "https://storage.example.com/file.txt", "filename": "guide.txt"},
            )

    response = asyncio.run(import_document())

    assert response.status_code == 201
    assert response.json() == {"files": 1, "chunks": 2, "total_chunks": 2}
    assert len(list(upload_dir.glob("*.txt"))) == 1
    assert _DownloadClient.last_kwargs["verify"] is False


def test_member_cannot_import_document_from_cloud_storage_url(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    token = create_access_token(User(id="member-id", openid="member", role="member"), "test-signing-secret-with-32-bytes")

    async def import_document() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/import-url",
                headers={"Authorization": f"Bearer {token}"},
                json={"url": "https://storage.example.com/file.txt", "filename": "guide.txt"},
            )

    response = asyncio.run(import_document())
    assert response.status_code == 403


def test_import_document_rejects_non_https_source(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    async def import_document() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/import-url",
                headers={"Authorization": f"Bearer {token}"},
                json={"url": "http://storage.example.com/file.txt", "filename": "guide.txt"},
            )

    response = asyncio.run(import_document())
    assert response.status_code == 422


def test_import_document_rejects_private_storage_address(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    async def import_document() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/import-url",
                headers={"Authorization": f"Bearer {token}"},
                json={"url": "https://127.0.0.1/file.txt", "filename": "guide.txt"},
            )

    response = asyncio.run(import_document())
    assert response.status_code == 422


def test_import_document_rejects_oversized_storage_response(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    from api.services import files

    monkeypatch.setattr(files.httpx, "Client", _LargeDownloadClient)
    token = create_access_token(User(id="admin-id", openid="admin", role="admin"), "test-signing-secret-with-32-bytes")

    async def import_document() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/v1/documents/import-url",
                headers={"Authorization": f"Bearer {token}"},
                json={"url": "https://storage.example.com/file.txt", "filename": "guide.txt"},
            )

    response = asyncio.run(import_document())
    assert response.status_code == 413


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
