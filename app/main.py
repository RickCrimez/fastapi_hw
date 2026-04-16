from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import advertisements
from app.exceptions import register_exception_handlers
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Advertisement Service",
    description="Сервис объявлений купли/продажи с пагинацией и поиском",
    version="2.0.0",
    lifespan=lifespan
)

register_exception_handlers(app)

app.include_router(advertisements.router)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Advertisement Service is running",
        "version": "2.0.0",
        "endpoints": {
            "create": "POST /advertisement",
            "update": "PATCH /advertisement/{id}",
            "delete": "DELETE /advertisement/{id}",
            "get_by_id": "GET /advertisement/{id}",
            "search": "GET /advertisement/?title=&author=&min_price=&max_price=&limit=&offset="
        },
        "documentation": "/docs",
        "alternative_docs": "/redoc"
    }