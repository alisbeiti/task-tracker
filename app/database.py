from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# `check_same_thread=False` is required for SQLite when used with FastAPI,
# since FastAPI may access the database from a different thread than the
# one that created the connection.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all future ORM models will inherit from.
Base = declarative_base()


def init_db() -> None:
    """
    Create all database tables based on models registered against Base.

    Currently there are no models defined yet (CRUD/entities come in a
    later module), so this creates an empty SQLite database file if one
    doesn't already exist. Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI dependency that provides a database session per request,
    and ensures it is closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()