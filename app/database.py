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
    """Create all database tables registered against ``Base``, if missing.

    Safe to call multiple times.

    [VERIFY]: no ORM models are currently registered against ``Base``,
    so this presently creates an empty SQLite database file with no
    tables. Task data is stored in-memory via ``app.storage`` rather
    than through this database/engine — confirm whether that split is
    intentional or ``app.storage`` is meant to be migrated onto this
    database later.

    Returns:
        None.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that provides a database session per request.

    Yields:
        Session: A SQLAlchemy session, closed automatically once the
            request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()