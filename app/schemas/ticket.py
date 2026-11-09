from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    priority: Literal["low", "medium", "high", "urgent"]
    category: str = Field(min_length=2, max_length=100)


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    category: str
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    due_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    body: str
    is_internal: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: list[CommentResponse] = []


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    is_internal: bool = False


class TicketAssign(BaseModel):
    assigned_to: int


class TicketStatusUpdate(BaseModel):
    status: Literal[
        "open",
        "in_progress",
        "resolved",
        "closed",
    ]


class SLAReportItem(BaseModel):
    ticket_id: int
    title: str
    priority: str
    due_at: datetime
    hours_overdue: float
    assigned_to: int | None
