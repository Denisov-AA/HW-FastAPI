# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app
from db.db import create_initial_users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.db import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    create_initial_users(db)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_login(test_client):
    response = test_client.post("/login", json={"username": "user1", "password": "password1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Authentication successful"}


def test_login_invalid_user(test_client):
    response = test_client.post("/login", json={"username": "invalid_user", "password": "password"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_model_fit(test_client):
    response = test_client.post("/model_fit", json={"username": "user1", "password": "password1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Model successfully trained and saved"}
