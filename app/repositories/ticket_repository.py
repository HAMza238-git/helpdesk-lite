from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Comment, Ticket, User


async def create_ticket(
    session: AsyncSession,
    ticket: Ticket,
) -> Ticket:
    session.add(ticket)
    await session.flush()
    return ticket


async def list_tickets(
    session: AsyncSession,
    employee_id: int | None,
    status_filter: str | None,
    priority_filter: str | None,
    assigned_to: int | None,
    offset: int,
    limit: int,
) -> tuple[list[Ticket], int]:

    query = select(Ticket)
    count_query = select(func.count()).select_from(Ticket)

    if employee_id is not None:
        query = query.where(Ticket.created_by == employee_id)
        count_query = count_query.where(Ticket.created_by == employee_id)

    if status_filter:
        query = query.where(Ticket.status == status_filter)
        count_query = count_query.where(Ticket.status == status_filter)

    if priority_filter:
        query = query.where(Ticket.priority == priority_filter)
        count_query = count_query.where(Ticket.priority == priority_filter)

    if assigned_to is not None:
        query = query.where(Ticket.assigned_to == assigned_to)
        count_query = count_query.where(Ticket.assigned_to == assigned_to)

    total_result = await session.execute(count_query)
    total_count = total_result.scalar_one()

    ticket_result = await session.execute(
        query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit)
    )

    tickets = list(ticket_result.scalars().all())

    return tickets, total_count


async def get_ticket_with_comments(
    session: AsyncSession,
    ticket_id: int,
) -> Ticket | None:

    result = await session.execute(
        select(Ticket)
        .options(selectinload(Ticket.comments))
        .where(Ticket.id == ticket_id)
    )

    return result.scalar_one_or_none()


async def create_comment(
    session: AsyncSession,
    comment: Comment,
) -> Comment:
    session.add(comment)
    await session.flush()
    return comment


async def get_ticket_for_update(
    session: AsyncSession,
    ticket_id: int,
) -> Ticket | None:
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id).with_for_update()
    )
    return result.scalar_one_or_none()


async def get_agent_for_update(
    session: AsyncSession,
    agent_id: int,
) -> User | None:
    result = await session.execute(
        select(User).where(User.id == agent_id).with_for_update()
    )
    return result.scalar_one_or_none()


async def count_agent_in_progress_tickets(
    session: AsyncSession,
    agent_id: int,
    exclude_ticket_id: int,
) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(Ticket)
        .where(
            Ticket.assigned_to == agent_id,
            Ticket.status == "in_progress",
            Ticket.id != exclude_ticket_id,
        )
    )
    return result.scalar_one()


async def get_overdue_tickets(session: AsyncSession):
    now = datetime.now(UTC)

    result = await session.execute(
        select(Ticket)
        .where(
            Ticket.status == "open",
            Ticket.due_at < now,
        )
        .order_by(Ticket.due_at.asc())
    )

    return list(result.scalars().all())
