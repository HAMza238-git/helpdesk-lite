from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.ticket_repository import (
    get_ticket_with_comments,
)
from app.schemas.ticket import (
    CommentResponse,
    TicketDetailResponse,
)


async def get_ticket_details(
    session: AsyncSession,
    ticket_id: int,
    current_user: User,
) -> TicketDetailResponse:

    ticket = await get_ticket_with_comments(
        session,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if current_user.role == "employee" and ticket.created_by != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    ticket_response = TicketDetailResponse.model_validate(ticket)

    visible_comments = [
        CommentResponse.model_validate(comment)
        for comment in ticket.comments
        if (current_user.role != "employee" or not comment.is_internal)
    ]

    return ticket_response.model_copy(update={"comments": visible_comments})
