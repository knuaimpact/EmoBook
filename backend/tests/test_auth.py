from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.model.user import User
from app.service.auth_service import AuthService


def test_signup_flow(client: TestClient, db: Session):
    # Test Signup API
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user_id" in data

    # Verify DB state
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.name == "Test User"


def test_login_flow(client: TestClient, db: Session):
    # Setup user
    auth_service = AuthService(db)
    user = User(
        email="test@example.com",
        password_hash=auth_service.get_password_hash("password123"),
        name="Test User",
    )
    db.add(user)
    db.commit()

    # Test Login API
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data


def test_child_profile_flow(client: TestClient, db: Session):
    # Setup user and get token
    auth_service = AuthService(db)
    user = User(
        email="test@example.com",
        password_hash=auth_service.get_password_hash("password123"),
        name="Test User",
    )
    db.add(user)
    db.commit()
    token = auth_service.create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile
    response = client.post(
        "/api/v1/child-profiles",
        headers=headers,
        json={"name": "Test Child", "age": 5, "preferred_style": "adventure"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Child"
    assert data["age"] == 5

    # Get profiles
    response = client.get("/api/v1/child-profiles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Child"
