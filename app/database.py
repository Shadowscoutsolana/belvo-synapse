from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Normalize DATABASE_URL for standard SQLAlchemy driver (psycopg2 for Postgres, sqlite3 for SQLite)
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+asyncpg"):
    db_url = db_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
elif db_url.startswith("sqlite+aiosqlite"):
    db_url = db_url.replace("sqlite+aiosqlite", "sqlite")

engine_args = {}
if db_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    db_url,
    echo=False,
    **engine_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    print("--> get_db creating SessionLocal", flush=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        print("--> get_db closing session", flush=True)
        db.close()
