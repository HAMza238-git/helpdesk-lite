from fastapi import FastAPI

from app.core.middleware import RequestTrackingMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.routers.auth import router as auth_router
from app.routers.reports import router as reports_router
from app.routers.tickets import router as tickets_router
from app.routers.users import router as users_router

app = FastAPI(
    title="HelpDesk Lite",
    description="IT Support Ticket Management API",
    version="1.0.0",
)

app.add_middleware(RequestTrackingMiddleware)
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)
app.include_router(reports_router)


@app.get("/")
async def root():
    return {"message": "Welcome to HelpDesk Lite API"}
