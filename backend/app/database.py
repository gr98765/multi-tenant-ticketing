import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def normalize_db_url(url: str) -> str:
    """Point every Postgres URL at the psycopg 3 driver.

    Hosts like Render hand out ``postgres://`` URLs, and SQLAlchemy 2.1
    changed which driver a bare ``postgresql://`` URL uses, so we pin it.
    """
    for prefix in ("postgres://", "postgresql://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


DATABASE_URL = normalize_db_url(os.getenv(
    "DATABASE_URL",
    "postgresql://ticketing:ticketing@localhost:5432/ticketing_db",
))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
