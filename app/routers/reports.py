from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models import User
from app.schemas.ticket import SLAReportItem
from app.services.sla_service import get_sla_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/sla",
    response_model=list[SLAReportItem],
)
async def sla_report(
    current_user: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
):
    return await get_sla_report(session)
