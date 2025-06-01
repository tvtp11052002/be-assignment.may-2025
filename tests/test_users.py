# Test user-related functionality
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user():
    response = client.post("/users/", json={"email": "test@example.com", "name": "Test User"})
    assert response.status_code == 201
    return response.json()

def test_create_user(test_user):
    assert "id" in test_user
    assert test_user["email"] == "test@example.com"

def test_get_user_by_id():
    # Tạo user
    create = client.post("/users/", json={"email": "get@example.com", "name": "Get User"})
    user = create.json()

    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "get@example.com"

def test_list_users():
    # Tạo ít nhất 1 user trước
    client.post("/users/", json={"email": "list@example.com", "name": "List User"})

    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_delete_all_users():
    # Tạo vài user
    client.post("/users/", json={"email": "a@example.com", "name": "A"})
    client.post("/users/", json={"email": "b@example.com", "name": "B"})

    # Xoá tất cả
    response = client.delete("/users/")
    assert response.status_code == 204

    # Kiểm tra list user rỗng
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []
