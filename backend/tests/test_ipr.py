import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from softwarepassport.app import app, get_db
from softwarepassport.database import Base


engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_index(test_db):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "openapi", "path": "/openapi.json"},
        {"name": "swagger_ui_html", "path": "/docs"},
        {"name": "swagger_ui_redirect", "path": "/docs/oauth2-redirect"},
        {"name": "redoc_html", "path": "/redoc"},
        {"name": "root", "path": "/"},
        {"name": "list_all_projects", "path": "/projects"},
        {"name": "create_or_update_a_new_project", "path": "/project"},
        {"name": "scan", "path": "/scan"},
        {"name": "status", "path": "/status"},
    ]
