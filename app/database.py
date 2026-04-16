from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, что переменная окружения задана
if not DATABASE_URL:
    print("=" * 60)
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Please set DATABASE_URL in .env file or environment variables")
    print("Example: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname")
    print("=" * 60)
    sys.exit(1)

# Проверяем корректность формата URL
if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite:///")):
    print("=" * 60)
    print(f"ERROR: Invalid DATABASE_URL format: {DATABASE_URL}")
    print("DATABASE_URL should start with:")
    print("  - postgresql:// for PostgreSQL")
    print("  - sqlite:/// for SQLite")
    print("=" * 60)
    sys.exit(1)

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Проверка соединения перед использованием
        echo=False,  # Установите True для логирования SQL запросов
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print(f"✓ Database engine created successfully for: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    print("=" * 60)
    print(f"ERROR: Failed to create database engine: {e}")
    print("Please check your database connection and credentials")
    print("=" * 60)
    sys.exit(1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()