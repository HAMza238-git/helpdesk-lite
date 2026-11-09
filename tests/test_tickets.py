import pytest


async def register_and_login(client, email):
    await client.post(
        "/auth/register",
        json={
            "name": "Test Employee",
            "email": email,
            "password": "Test@12345",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@12345",
        },
    )

    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_ticket(client):
    token = await register_and_login(client, "ticket@example.com")

    response = await client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Laptop is not working",
            "description": "My laptop does not start when I press the power button.",
            "priority": "high",
            "category": "Hardware",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Laptop is not working"
    assert response.json()["status"] == "open"


@pytest.mark.asyncio
async def test_employee_sees_only_own_tickets(client):
    token_one = await register_and_login(client, "employee1@example.com")
    token_two = await register_and_login(client, "employee2@example.com")

    await client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {token_one}"},
        json={
            "title": "My laptop problem",
            "description": "My laptop is not starting properly.",
            "priority": "medium",
            "category": "Hardware",
        },
    )

    await client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {token_two}"},
        json={
            "title": "My internet problem",
            "description": "My internet connection is not working.",
            "priority": "low",
            "category": "Network",
        },
    )

    response = await client.get(
        "/tickets",
        headers={"Authorization": f"Bearer {token_one}"},
    )

    assert response.status_code == 200

    tickets = response.json()["tickets"]

    assert len(tickets) == 1
    assert tickets[0]["title"] == "My laptop problem"


@pytest.mark.asyncio
async def test_ticket_requires_authentication(client):
    response = await client.get("/tickets")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_employee_cannot_view_another_users_ticket(client):
    token_one = await register_and_login(client, "owner@example.com")
    token_two = await register_and_login(client, "other@example.com")

    create_response = await client.post(
        "/tickets",
        headers={"Authorization": f"Bearer {token_one}"},
        json={
            "title": "Private employee ticket",
            "description": "This ticket belongs to another employee.",
            "priority": "medium",
            "category": "Hardware",
        },
    )

    ticket_id = create_response.json()["id"]

    response = await client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token_two}"},
    )

    assert response.status_code == 404
