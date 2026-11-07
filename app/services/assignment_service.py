from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.ticket_repository import (
    count_agent_in_progress_tickets,
    get_agent_for_update,
    get_ticket_for_update,
)


async def assign_ticket(
    session: AsyncSession,
    ticket_id: int,
    agent_id: int,
):
    ticket = await get_ticket_for_update(session, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    agent = await get_agent_for_update(session, agent_id)

    if agent is None or agent.role != "agent" or not agent.is_active:
        raise HTTPException(
            status_code=400,
            detail="Assigned user must be an active agent",
        )

    active_count = await count_agent_in_progress_tickets(
        session,
        agent_id,
        ticket_id,
    )

    if active_count >= 5:
        raise HTTPException(
            status_code=409,
            detail="Agent already has 5 in-progress tickets",
        )

    ticket.assigned_to = agent_id

    await session.commit()
    await session.refresh(ticket)

    return ticket
