from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import advertisements, users, auth
from app.exceptions import register_exception_handlers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Advertisement Service",
    description="Сервис объявлений купли/продажи с авторизацией и пагинацией",
    version="3.0.0",
    lifespan=lifespan
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(advertisements.router)

@app.get("/")
async def root():
    return {
        "message": "Advertisement Service is running",
        "version": "3.0.0",
        "endpoints": {
            "auth": "POST /login",
            "users": "GET/POST/PATCH/DELETE /user",
            "advertisements": "GET/POST/PATCH/DELETE /advertisement"
        },
        "documentation": "/docs"
    }