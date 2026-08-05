import asyncio

import httpx

from api.main import create_app


def test_health_check_reports_service_ready():
    async def request_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/v1/health")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_allows_local_development_origin():
    async def preflight() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.options(
                "/api/v1/health",
                headers={
                    "Origin": "http://localhost",
                    "Access-Control-Request-Method": "GET",
                },
            )

    response = asyncio.run(preflight())

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost"
