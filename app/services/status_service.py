from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.ticket_repository import (
    count_agent_in_progress_tickets,
    get_agent_for_update,
    get_ticket_for_update,
)


async def update_ticket_status(
    session: AsyncSession,
    ticket_id: int,
    new_status: str,
):
    ticket = await get_ticket_for_update(session, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    allowed_transitions = {
        "open": ["in_progress"],
        "in_progress": ["resolved"],
        "resolved": ["closed", "in_progress"],
        "closed": [],
    }

    if new_status not in allowed_transitions[ticket.status]:
        raise HTTPException(
            status_code=409,
            detail="Invalid status transition",
        )

    if new_status == "in_progress" and ticket.assigned_to is not None:
        await get_agent_for_update(session, ticket.assigned_to)

        active_count = await count_agent_in_progress_tickets(
            session,
            ticket.assigned_to,
            ticket_id,
        )

        if active_count >= 5:
            raise HTTPException(
                status_code=409,
                detail="Agent already has 5 in-progress tickets",
            )

    ticket.status = new_status

    if new_status == "resolved":
        ticket.resolved_at = datetime.now(UTC)

    elif new_status == "in_progress":
        ticket.resolved_at = None

    await session.commit()
    await session.refresh(ticket)

    return ticket
