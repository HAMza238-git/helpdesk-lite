from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.tickets import router as tickets_router
from app.routers.users import router as users_router

app = FastAPI(
    title="HelpDesk Lite",
    description="IT Support Ticket Management API",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)


@app.get("/")
async def root():
    return {"message": "Welcome to HelpDesk Lite API"}
