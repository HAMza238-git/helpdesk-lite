import pytest


@pytest.mark.asyncio
async def test_request_tracking_headers(client):
    response = await client.get("/tickets")

    assert response.status_code == 401
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers

    process_time = float(response.headers["X-Process-Time-Ms"])
    assert process_time >= 0


@pytest.mark.asyncio
async def test_custom_request_id_is_preserved(client):
    custom_id = "test-request-123"

    response = await client.get(
        "/tickets",
        headers={"X-Request-ID": custom_id},
    )

    assert response.headers["X-Request-ID"] == custom_id
