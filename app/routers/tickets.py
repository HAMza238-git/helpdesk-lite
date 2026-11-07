from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import User
from app.schemas.ticket import (
    CommentCreate,
    CommentResponse,
    TicketAssign,
    TicketCreate,
    TicketDetailResponse,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdate,
)
from app.services.assignment_service import assign_ticket
from app.services.comment_service import add_ticket_comment
from app.services.status_service import update_ticket_status
from app.services.ticket_detail_service import get_ticket_details
from app.services.ticket_list_service import get_ticket_list
from app.services.ticket_service import create_new_ticket

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_endpoint(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await create_new_ticket(
        session,
        ticket_data,
        current_user.id,
    )


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    status_filter: Literal["open", "in_progress", "resolved", "closed"] | None = Query(
        default=None, alias="status"
    ),
    priority: Literal["low", "medium", "high", "urgent"] | None = None,
    assigned_to: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await get_ticket_list(
        session=session,
        current_user=current_user,
        status_filter=status_filter,
        priority_filter=priority,
        assigned_to=assigned_to,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket_detail(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await get_ticket_details(
        session=session,
        ticket_id=ticket_id,
        current_user=current_user,
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def create_ticket_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await add_ticket_comment(
        session=session,
        ticket_id=ticket_id,
        comment_data=comment_data,
        current_user=current_user,
    )


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket_endpoint(
    ticket_id: int,
    assignment: TicketAssign,
    current_user: User = Depends(require_roles("agent", "admin")),
    session: AsyncSession = Depends(get_db),
):
    return await assign_ticket(
        session=session,
        ticket_id=ticket_id,
        agent_id=assignment.assigned_to,
    )


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def change_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    current_user: User = Depends(require_roles("agent", "admin")),
    session: AsyncSession = Depends(get_db),
):
    return await update_ticket_status(
        session=session,
        ticket_id=ticket_id,
        new_status=status_data.status,
    )
