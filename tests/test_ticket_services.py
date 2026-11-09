
import pytest
from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import AsyncMock

import app.services.assignment_service as assignment_service
import app.services.status_service as status_service


def make_session():
    return SimpleNamespace(
        commit=AsyncMock(),
        refresh=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_assign_ticket_success(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(assigned_to=None)
    agent = SimpleNamespace(role="agent", is_active=True)

    monkeypatch.setattr(
        assignment_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )
    monkeypatch.setattr(
        assignment_service,
        "get_agent_for_update",
        AsyncMock(return_value=agent),
    )
    monkeypatch.setattr(
        assignment_service,
        "count_agent_in_progress_tickets",
        AsyncMock(return_value=2),
    )

    result = await assignment_service.assign_ticket(session, 1, 10)

    assert result.assigned_to == 10
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(ticket)


@pytest.mark.asyncio
async def test_assign_ticket_not_found(monkeypatch):
    session = make_session()

    monkeypatch.setattr(
        assignment_service,
        "get_ticket_for_update",
        AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await assignment_service.assign_ticket(session, 999, 10)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "is_active"),
    [
        ("employee", True),
        ("agent", False),
        ("admin", True),
    ],
)
async def test_assign_ticket_invalid_agent(monkeypatch, role, is_active):
    session = make_session()
    ticket = SimpleNamespace(assigned_to=None)
    agent = SimpleNamespace(role=role, is_active=is_active)

    monkeypatch.setattr(
        assignment_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )
    monkeypatch.setattr(
        assignment_service,
        "get_agent_for_update",
        AsyncMock(return_value=agent),
    )

    with pytest.raises(HTTPException) as exc:
        await assignment_service.assign_ticket(session, 1, 10)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_assign_ticket_agent_capacity_reached(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(assigned_to=None)
    agent = SimpleNamespace(role="agent", is_active=True)

    monkeypatch.setattr(
        assignment_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )
    monkeypatch.setattr(
        assignment_service,
        "get_agent_for_update",
        AsyncMock(return_value=agent),
    )
    monkeypatch.setattr(
        assignment_service,
        "count_agent_in_progress_tickets",
        AsyncMock(return_value=5),
    )

    with pytest.raises(HTTPException) as exc:
        await assignment_service.assign_ticket(session, 1, 10)

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_status_ticket_not_found(monkeypatch):
    session = make_session()

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await status_service.update_ticket_status(session, 999, "in_progress")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_status_invalid_transition(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(status="open", assigned_to=None)

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )

    with pytest.raises(HTTPException) as exc:
        await status_service.update_ticket_status(session, 1, "resolved")

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_status_success(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(
        status="open",
        assigned_to=None,
        resolved_at=None,
    )

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )

    result = await status_service.update_ticket_status(
        session, 1, "in_progress"
    )

    assert result.status == "in_progress"
    assert result.resolved_at is None
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolving_ticket_sets_resolved_at(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(
        status="in_progress",
        assigned_to=None,
        resolved_at=None,
    )

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )

    result = await status_service.update_ticket_status(
        session, 1, "resolved"
    )

    assert result.status == "resolved"
    assert result.resolved_at is not None


@pytest.mark.asyncio
async def test_reopening_ticket_clears_resolved_at(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(
        status="resolved",
        assigned_to=None,
        resolved_at="previous-resolution",
    )

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )

    result = await status_service.update_ticket_status(
        session, 1, "in_progress"
    )

    assert result.status == "in_progress"
    assert result.resolved_at is None


@pytest.mark.asyncio
async def test_status_change_respects_agent_capacity(monkeypatch):
    session = make_session()
    ticket = SimpleNamespace(
        status="open",
        assigned_to=10,
        resolved_at=None,
    )

    monkeypatch.setattr(
        status_service,
        "get_ticket_for_update",
        AsyncMock(return_value=ticket),
    )
    monkeypatch.setattr(
        status_service,
        "get_agent_for_update",
        AsyncMock(return_value=SimpleNamespace()),
    )
    monkeypatch.setattr(
        status_service,
        "count_agent_in_progress_tickets",
        AsyncMock(return_value=5),
    )

    with pytest.raises(HTTPException) as exc:
        await status_service.update_ticket_status(
            session, 1, "in_progress"
        )

    assert exc.value.status_code == 409
