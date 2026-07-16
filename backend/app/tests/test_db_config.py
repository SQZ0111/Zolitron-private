import importlib
import os


def test_postgres_database_url_is_normalized(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@localhost:5432/zolitron")

    import app.db as db_module

    importlib.reload(db_module)

    assert str(db_module.engine.url) == "postgresql+psycopg2://user:password@localhost:5432/zolitron"
