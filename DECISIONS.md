# Technical Decisions – HelpDesk Lite

This document explains the main database and application design decisions.

## 1. Database: PostgreSQL

**Decision:** PostgreSQL was selected as the relational database.

**Reason:**
- Supports foreign keys and relational integrity.
- Provides transactions and row-level locking.
- Works well with SQLAlchemy and asynchronous database access.
- Supports indexes and check constraints.

## 2. SQLAlchemy 2.0 Async

**Decision:** Use SQLAlchemy 2.0 with asynchronous sessions and the asyncpg driver.

**Reason:**
- Supports asynchronous database operations.
- Integrates with FastAPI.
- Provides ORM relationships and transaction management.
- Helps avoid blocking the event loop during database operations.

## 3. Foreign Keys and Cascading Deletes

**Decision:**
- Ticket creator and assignee reference users.
- Comments reference tickets and authors.
- Notifications reference users and tickets.
- Ticket deletion cascades to its comments.
- User deletion does not cascade to tickets or comments.

**Reason:**

This preserves user records and prevents accidental loss of ticket history. Comments are dependent on their ticket, so deleting a ticket removes its comments.

## 4. Database Check Constraints

**Decision:** Use database check constraints for valid roles, priorities, and statuses.

**Reason:**

Application validation alone is not sufficient. Database constraints provide an additional layer of protection against invalid values.

## 5. Unique Email Constraint

**Decision:** User email addresses must be unique.

**Reason:**

Each account must have a unique login identity. The database enforces this even when multiple requests attempt registration concurrently.

## 6. Indexes

**Decision:** Add indexes to frequently searched and filtered columns.

| Index | Reason |
|---|---|
| Users email | Faster login and email lookup |
| Tickets status | Faster status filtering |
| Tickets priority | Faster priority filtering |
| Tickets assigned_to + status | Faster agent workload queries |
| Comments ticket_id + created_at | Faster ticket comment retrieval |
| Notifications user_id + created_at | Faster user notification retrieval |

Indexes improve read performance but add storage and write overhead, so they are added for expected query patterns.

## 7. Ticket Assignment Concurrency

**Decision:** Use SELECT FOR UPDATE to lock the agent row during assignment capacity checks.

**Reason:**

An agent is limited to five in-progress tickets. Without locking, simultaneous requests could both see available capacity and exceed the limit.

Locking the agent row serializes competing assignments for that agent.

The assignment operation is performed within a database transaction.

## 8. Ticket Status Workflow

**Decision:** Enforce allowed status transitions in the service layer.

**Allowed transitions:**
- Open → In Progress
- In Progress → Resolved
- Resolved → Closed
- Resolved → In Progress

**Reason:**

A controlled workflow prevents invalid ticket states. Invalid transitions return HTTP 409 Conflict.

The resolved timestamp is set when a ticket is resolved and cleared when it is reopened.

## 9. Role-Based Access Control

**Decision:** Use three roles: employee, agent, and admin.

**Reason:**
- Employees create and view their own tickets.
- Agents manage assigned support work.
- Admins have administrative and reporting permissions.

Public registration always creates an employee account to prevent privilege escalation.

## 10. Background Notifications

**Decision:** Use FastAPI BackgroundTasks for assignment and resolution notifications.

**Reason:**

Notifications do not need to delay the original API response. A separate database session is used for each background notification operation.

Failures are logged without failing the original ticket request.

**Limitation:** FastAPI BackgroundTasks are in-process tasks, not a durable job queue. A process shutdown can interrupt pending work.

## 11. Authentication

**Decision:** Use bcrypt password hashing and JWT bearer authentication.

**Reason:**
- Passwords are stored as hashes rather than plaintext.
- JWT provides stateless access-token authentication.
- User roles are included in the token and the active user is loaded from the database for authorization.

## 12. Separate Test Database

**Decision:** Use a dedicated PostgreSQL database for automated tests.

**Reason:**

Tests must not modify development data. The test database is isolated and its schema is prepared for test execution.

## 13. Request Tracking

**Decision:** Add request ID and processing-time middleware.

**Reason:**

Request IDs help correlate API requests with application logs. Processing-time headers help measure request performance.

Unexpected exceptions are logged with their request ID and return a generic HTTP 500 response.

## 14. Database Migrations

**Decision:** Use Alembic for schema versioning.

**Reason:**

Migrations provide a controlled way to apply and reverse database schema changes across development and deployment environments.