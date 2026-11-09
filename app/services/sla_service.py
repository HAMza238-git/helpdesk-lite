from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.ticket_repository import get_overdue_tickets


async def get_sla_report(session: AsyncSession):
    tickets = await get_overdue_tickets(session)
    now = datetime.now(UTC)

    report = []

    for ticket in tickets:
        hours_overdue = (now - ticket.due_at).total_seconds() / 3600

        report.append(
            {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "priority": ticket.priority,
                "due_at": ticket.due_at,
                "hours_overdue": round(hours_overdue, 2),
                "assigned_to": ticket.assigned_to,
            }
        )

    return report
