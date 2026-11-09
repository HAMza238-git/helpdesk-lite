import logging

from app.core.database import AsyncSessionLocal
from app.models import Notification

logger = logging.getLogger(__name__)


async def create_notification(
    user_id: int,
    ticket_id: int,
    message: str,
):
    try:
        async with AsyncSessionLocal() as session:
            notification = Notification(
                user_id=user_id,
                ticket_id=ticket_id,
                message=message,
            )

            session.add(notification)
            await session.commit()

            logger.info(
                "Notification created for user %s, ticket %s",
                user_id,
                ticket_id,
            )

    except Exception:
        logger.exception(
            "Failed to create notification for user %s, ticket %s",
            user_id,
            ticket_id,
        )
