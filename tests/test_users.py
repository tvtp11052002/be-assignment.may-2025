# Test user-related functionality
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user():
    response = client.post(
        "/users/", json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 201
    return response.json()

#### User Management ####
# Create usser
def test_create_user(test_user):
    assert "id" in test_user
    assert test_user["email"] == "test@example.com"

# Get usser by ID
def test_get_user_by_id():
    # Tạo user
    create = client.post(
        "/users/", json={"email": "get@example.com", "name": "Get User"}
    )
    user = create.json()

    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "get@example.com"

# Lisst ussers
def test_list_users():
    client.post("/users/", json={"email": "list@example.com", "name": "List User"})

    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# Optional: Delete all users
def test_delete_all_users():
    client.post("/users/", json={"email": "a@example.com", "name": "A"})
    client.post("/users/", json={"email": "b@example.com", "name": "B"})

    response = client.delete("/users/")
    assert response.status_code == 204

    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []
