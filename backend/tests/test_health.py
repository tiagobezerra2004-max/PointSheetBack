import asyncio

import httpx

from app.api import health
from app.core.database import DatabaseUnavailable
from app.main import app


def request(
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, headers=headers)

    return asyncio.run(send())


def test_health_returns_ok_when_database_is_available(monkeypatch) -> None:
    monkeypatch.setattr(health, "check_database_connection", lambda: None)

    response = request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_standard_error_when_database_is_unavailable(monkeypatch) -> None:
    def unavailable() -> None:
        raise DatabaseUnavailable

    monkeypatch.setattr(health, "check_database_connection", unavailable)

    response = request("GET", "/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert "senha" not in response.text.lower()


def test_cors_allows_configured_frontend_origin(monkeypatch) -> None:
    monkeypatch.setattr(health, "check_database_connection", lambda: None)

    response = request(
        "OPTIONS",
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_swagger_openapi_is_enabled() -> None:
    docs_response = request("GET", "/docs")
    response = request("GET", "/openapi.json")

    assert docs_response.status_code == 200
    assert response.status_code == 200
    assert "/health" in response.json()["paths"]


def test_http_errors_use_standard_json_envelope() -> None:
    response = request("GET", "/rota-inexistente")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.json()["error"]["message"]
