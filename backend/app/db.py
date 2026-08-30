import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def normalize_database_url(database_url: str) -> str:
    """Convert Render's legacy Postgres scheme into SQLAlchemy's driver URL."""
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    return database_url


DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./zolitron.db")
)

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    from app.models import analysis_run, category, classification, detection, image, label

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
