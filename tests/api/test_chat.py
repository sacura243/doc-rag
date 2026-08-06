import asyncio

import httpx

from api.main import create_app
from api.services.auth import create_access_token
from api.services.users import User


def test_authenticated_user_receives_answer_with_safe_source_name(monkeypatch, tmp_path):
    monkeypatch.setenv("API_DATABASE_PATH", str(tmp_path / "users.sqlite3"))
    monkeypatch.setenv("API_JWT_SECRET", "test-signing-secret-with-32-bytes")
    from api.routers import chat

    monkeypatch.setattr(chat, "load_config", lambda: __import__("doc_rag.config", fromlist=["Config"]).Config())
    monkeypatch.setattr(chat, "ask_with_sources", lambda *_args, **_kwargs: ("answer", [{"source": r"D:\secret\guide.txt", "page": 2, "content": "evidence"}]))
    token = create_access_token(User(id="member-id", openid="member", role="member"), "test-signing-secret-with-32-bytes")

    async def ask() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/v1/chat", headers={"Authorization": f"Bearer {token}"}, json={"question": "test question", "top_k": 3})

    response = asyncio.run(ask())

    assert response.status_code == 200
    assert response.json() == {"answer": "answer", "sources": [{"name": "guide.txt", "page": 2, "content": "evidence"}]}
