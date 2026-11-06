import asyncio
import csv
import logging
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.exceptions.csv_exceptions import InvalidCSVRowError
from app.models import Ticket, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FILE = Path("data/tickets.csv")
BATCH_SIZE = 50


def calculate_due_date(priority: str) -> datetime:
    hours = {
        "urgent": 4,
        "high": 24,
        "medium": 72,
        "low": 168,
    }
    return datetime.now(UTC) + timedelta(hours=hours[priority])


def validate_csv_row(row: dict) -> None:
    required_fields = ["title", "description", "priority", "category"]

    for field in required_fields:
        if not row.get(field):
            raise InvalidCSVRowError(f"Missing {field}")

    if row["priority"] not in ["low", "medium", "high", "urgent"]:
        raise InvalidCSVRowError("Invalid priority")


def load_csv_tickets() -> list[dict]:
    tickets = []

    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            # Clean CSV headers and values
            row = {
                key.strip().lstrip("\ufeff"): value.strip() if value else value
                for key, value in row.items()
                if key is not None
            }

            try:
                validate_csv_row(row)
                tickets.append(row)

            except InvalidCSVRowError as error:
                logger.warning(
                    "Skipping CSV line %s: %s",
                    line_number,
                    error,
                )

    return tickets


async def create_users(session) -> tuple[User, list[User], list[User]]:
    existing_users = await session.scalars(select(User))

    if list(existing_users):
        raise RuntimeError(
            "Users already exist. Clear the database before seeding again."
        )

    admin = User(
        name="System Admin",
        email="admin@example.com",
        password_hash="$2b$12$replace_with_real_hash",
        role="admin",
    )

    agents = [
        User(
            name=f"Agent {number}",
            email=f"agent{number}@example.com",
            password_hash="$2b$12$replace_with_real_hash",
            role="agent",
        )
        for number in range(1, 4)
    ]

    employees = [
        User(
            name=f"Employee {number}",
            email=f"employee{number}@example.com",
            password_hash="$2b$12$replace_with_real_hash",
            role="employee",
        )
        for number in range(1, 11)
    ]

    session.add_all([admin, *agents, *employees])
    await session.flush()

    return admin, agents, employees


async def seed_database() -> None:
    async with AsyncSessionLocal() as session:
        try:
            _, _, employees = await create_users(session)

            csv_tickets = load_csv_tickets()

            if not csv_tickets:
                raise RuntimeError("No valid ticket rows found in CSV.")

            ticket_objects = []

            for number in range(120):
                row = random.choice(csv_tickets)
                employee = random.choice(employees)

                ticket = Ticket(
                    title=row["title"],
                    description=row["description"],
                    priority=row["priority"],
                    category=row["category"],
                    status="open",
                    created_by=employee.id,
                    assigned_to=None,
                    due_at=calculate_due_date(row["priority"]),
                )

                ticket_objects.append(ticket)

            for start in range(0, len(ticket_objects), BATCH_SIZE):
                batch = ticket_objects[start : start + BATCH_SIZE]

                session.add_all(batch)
                await session.flush()

                logger.info(
                    "Inserted batch of %s tickets",
                    len(batch),
                )

            await session.commit()

            logger.info(
                "Seed completed: 1 admin, 3 agents, 10 employees, %s tickets",
                len(ticket_objects),
            )

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
