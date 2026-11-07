from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticket
from app.repositories.ticket_repository import create_ticket
from app.schemas.ticket import TicketCreate

DUE_DATE_HOURS = {
    "urgent": 4,
    "high": 24,
    "medium": 72,
    "low": 168,
}


async def create_new_ticket(
    session: AsyncSession,
    ticket_data: TicketCreate,
    current_user_id: int,
) -> Ticket:

    due_at = datetime.now(UTC) + timedelta(hours=DUE_DATE_HOURS[ticket_data.priority])

    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        category=ticket_data.category,
        created_by=current_user_id,
        status="open",
        due_at=due_at,
    )

    await create_ticket(session, ticket)
    await session.commit()
    await session.refresh(ticket)

    return ticket
