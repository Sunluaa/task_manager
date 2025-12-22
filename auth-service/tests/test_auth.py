import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

def test_register_user(db):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert "id" in data

def test_register_duplicate_email(db):
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "testpass123",
            "full_name": "First User"
        }
    )
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "pass123",
            "full_name": "Second User"
        }
    )
    assert response.status_code == 400

def test_login_success(db):
    client.post(
        "/auth/register",
        json={
            "email": "login@test.com",
            "password": "testpass123",
            "full_name": "Login User"
        }
    )
    response = client.post(
        "/auth/login",
        json={
            "email": "login@test.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(db):
    client.post(
        "/auth/register",
        json={
            "email": "wrong@test.com",
            "password": "correctpass",
            "full_name": "Wrong Pass User"
        }
    )
    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@test.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_login_nonexistent_user(db):
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "password"
        }
    )
    assert response.status_code == 401

def test_get_users(db):
    client.post(
        "/auth/register",
        json={
            "email": "user1@test.com",
            "password": "pass123",
            "full_name": "User One"
        }
    )
    client.post(
        "/auth/register",
        json={
            "email": "user2@test.com",
            "password": "pass123",
            "full_name": "User Two"
        }
    )
    response = client.get("/auth/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(u["email"] == "user1@test.com" for u in data)
    assert any(u["email"] == "user2@test.com" for u in data)

def test_invalid_registration_data(db):
    response = client.post(
        "/auth/register",
        json={
            "email": "invalidemail",
            "password": "pass",
            "full_name": ""
        }
    )
    assert response.status_code == 422

def test_verify_token(db):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "verify@test.com",
            "password": "verifypass",
            "full_name": "Verify User"
        }
    )
    login_response = client.post(
        "/auth/login",
        json={
            "email": "verify@test.com",
            "password": "verifypass"
        }
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "verify@test.com"

def test_verify_invalid_token(db):
    response = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
