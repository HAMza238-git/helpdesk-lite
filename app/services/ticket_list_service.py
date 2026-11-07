from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.ticket_repository import list_tickets


async def get_ticket_list(
    session: AsyncSession,
    current_user: User,
    status_filter: str | None,
    priority_filter: str | None,
    assigned_to: int | None,
    page: int,
    page_size: int,
):

    employee_id = current_user.id if current_user.role == "employee" else None

    offset = (page - 1) * page_size

    tickets, total_count = await list_tickets(
        session=session,
        employee_id=employee_id,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assigned_to=assigned_to,
        offset=offset,
        limit=page_size,
    )

    return {
        "tickets": tickets,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "has_next": offset + len(tickets) < total_count,
    }
