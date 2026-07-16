from app.db import normalize_database_url


def test_postgres_database_url_is_normalized():
    assert normalize_database_url(
        "postgres://user:password@localhost:5432/zolitron"
    ) == "postgresql+psycopg2://user:password@localhost:5432/zolitron"
