from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.pool import NullPool


from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
    isolation_level="AUTOCOMMIT",
)
SessionLocal = sessionmaker(bind=engine, autocommit=True)
Base = declarative_base()
