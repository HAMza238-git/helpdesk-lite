from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment, User
from app.repositories.ticket_repository import (
    create_comment,
    get_ticket_with_comments,
)
from app.schemas.ticket import CommentCreate, CommentResponse


async def add_ticket_comment(
    session: AsyncSession,
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: User,
) -> CommentResponse:

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

    if comment_data.is_internal and current_user.role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Employees cannot create internal comments",
        )

    comment = Comment(
        ticket_id=ticket_id,
        author_id=current_user.id,
        body=comment_data.body,
        is_internal=comment_data.is_internal,
    )

    await create_comment(session, comment)
    await session.commit()
    await session.refresh(comment)

    return CommentResponse.model_validate(comment)
