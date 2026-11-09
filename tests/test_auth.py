import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Test Employee",
            "email": "testemployee@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "testemployee@example.com"
    assert response.json()["role"] == "employee"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    user_data = {
        "name": "Test Employee",
        "email": "duplicate@example.com",
        "password": "Test@12345",
    }

    await client.post("/auth/register", json=user_data)
    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    await client.post(
        "/auth/register",
        json={
            "name": "Login Test",
            "email": "login@example.com",
            "password": "Correct@123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "Wrong@123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "name": "Login Success",
            "email": "success@example.com",
            "password": "Correct@123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "success@example.com",
            "password": "Correct@123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
