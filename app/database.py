from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("=" * 60)
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Please set DATABASE_URL in .env file")
    print("=" * 60)
    sys.exit(1)

if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite:///")):
    print("=" * 60)
    print(f"ERROR: Invalid DATABASE_URL format: {DATABASE_URL}")
    print("DATABASE_URL should start with postgresql:// or sqlite:///")
    print("=" * 60)
    sys.exit(1)

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print(f"✓ Database connected successfully")
except Exception as e:
    print(f"ERROR: Failed to connect to database: {e}")
    sys.exit(1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()