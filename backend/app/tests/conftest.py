import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

#This test is just for the ci-cd pipeline, it will create a temporary database for testing purposes. The database will be deleted after the tests are completed.

TEST_DATABASE_PATH = Path(tempfile.gettempdir()) / f"zolitron-test-{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"

from app.db import engine
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Run API tests with application startup and shutdown hooks enabled."""
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)
