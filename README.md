# HelpDesk Lite – IT Support Ticket API

A REST API for managing IT support tickets, users, assignments, comments, notifications, and SLA reporting.

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- JWT authentication
- Pytest and HTTPX
- Ruff
- uv

## Features

- User registration and login with JWT authentication.
- Role-based access control: employee, agent, and admin.
- Create, list, filter, and view support tickets.
- Ticket assignment with a maximum of five in-progress tickets per agent.
- Ticket status workflow and validation.
- Public and internal ticket comments.
- Background notifications when tickets are assigned or resolved.
- SLA reporting for overdue open tickets.
- Request ID and request processing-time middleware.
- Automated API tests using a separate test database.

## Project Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd helpdesk-lite
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Create and activate the virtual environment

On Windows PowerShell:

```powershell
uv venv
.venv\Scripts\Activate.ps1
```

### 4. Create PostgreSQL databases

Create these databases in PostgreSQL:

- `helpdesk_lite`
- `helpdesk_lite_test`

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/helpdesk_lite
TEST_DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/helpdesk_lite_test
SECRET_KEY=YOUR_SECRET_KEY
```

Use your own PostgreSQL password and a secure secret key.

Never commit `.env` or real credentials.

### 6. Run database migrations

```bash
uv run alembic upgrade head
```

### 7. Load seed data

```bash
uv run python -m app.seed
```

The seed script creates sample users and tickets.

### 8. Start the API

```bash
uv run uvicorn app.main:app --reload
```

API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Authentication

Register using:

`POST /auth/register`

Log in using:

`POST /auth/login`

Use the returned bearer access token to authorize protected endpoints.

Public registration creates employee accounts. Agent and admin roles must be assigned through an authorized administrative process.

## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register an employee |
| POST | `/auth/login` | Log in |
| GET | `/users/me` | Get current user |
| POST | `/tickets` | Create a ticket |
| GET | `/tickets` | List and filter tickets |
| GET | `/tickets/{ticket_id}` | Get ticket details |
| POST | `/tickets/{ticket_id}/comments` | Add a comment |
| POST | `/tickets/{ticket_id}/assign` | Assign a ticket |
| PATCH | `/tickets/{ticket_id}/status` | Update ticket status |
| GET | `/reports/sla` | Admin SLA report |

## Ticket Business Rules

### Ticket priorities and SLA targets

| Priority | SLA target |
|---|---|
| Urgent | 4 hours |
| High | 1 day |
| Medium | 3 days |
| Low | 7 days |

### Ticket status workflow

- Open → In Progress
- In Progress → Resolved
- Resolved → Closed
- Resolved → In Progress (reopen)

Invalid transitions return HTTP 409.

### Assignment rules

- Only agents and admins can assign tickets.
- Only active agents can receive assignments.
- An agent can have a maximum of five in-progress tickets.
- Agent-row locking protects concurrent assignment capacity checks.

### Access control

- Employees can view their own tickets only.
- Employees cannot see internal comments.
- Only agents and admins can create internal comments.
- Only admins can access SLA reporting.

## Notifications

FastAPI BackgroundTasks creates database notifications when:

- A ticket is assigned to an agent.
- A ticket is resolved, notifying its creator.

Notification failures are logged and do not fail the original ticket request.

## Running Automated Tests

Configure `TEST_DATABASE_URL` in `.env`, then run:

```bash
uv run python -m pytest -v
```

The test suite uses a separate test database.

## Code Quality

Run Ruff checks:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

## Database Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Check current migration:

```bash
uv run alembic current
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

