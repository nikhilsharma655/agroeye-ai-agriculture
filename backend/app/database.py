"""
SQLAlchemy engine/session setup. Works with PostgreSQL in production and
SQLite for local development (DATABASE_URL controls which).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables directly from models. Convenient for quick local/dev
    bootstrap and for the test suite, but NOT how production schema changes
    should be applied — use Alembic migrations for that (see backend/alembic/
    and `alembic upgrade head`). This function is a no-op no-schema-diff tool:
    it only creates missing tables and never alters existing ones."""
    from app.models import user, farm, crop, soil_record, weather_record, prediction, recommendation, alert, notification  # noqa: F401
    Base.metadata.create_all(bind=engine)
