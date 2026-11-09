
import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from app.main import app


async def unexpected_error_endpoint(request: Request):
    raise RuntimeError("Test unexpected error")


app.add_api_route(
    "/test-unexpected-error",
    unexpected_error_endpoint,
    methods=["GET"],
    name="test_unexpected_error",
)


@pytest.mark.asyncio
async def test_http_exception_includes_request_id(client):
    response = await client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()
    assert "request_id" in response.json()


@pytest.mark.asyncio
async def test_validation_exception_includes_request_id(client):
    response = await client.post("/auth/register", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    assert "request_id" in response.json()


@pytest.mark.asyncio
async def test_unexpected_exception_returns_500():
    transport = ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        response = await test_client.get("/test-unexpected-error")

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "request_id" in response.json()
