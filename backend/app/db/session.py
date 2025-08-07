from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None


def init_engine_and_create_all() -> None:
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        from app.db import models  # noqa: F401

        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

