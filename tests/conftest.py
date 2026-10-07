import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.utils import file_utils


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = (tmp_path / "test.db").as_posix()
    monkeypatch.setattr(file_utils, "GENERATED_DIR", tmp_path / "generated")
    application = create_app(f"sqlite:///{database_path}")
    with TestClient(application) as test_client:
        yield test_client