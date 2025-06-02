# Test message-related functionality
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


#### Messaging
@pytest.fixture(scope="module")
def test_data():
    sender = client.post(
        "/users/", json={"email": "tuanphong@gmail.com", "name": "Phong"}
    ).json()
    recipient_1 = client.post(
        "/users/", json={"email": "recipient_1@gmail.com", "name": "Recipient 1"}
    ).json()
    recipient_2 = client.post(
        "/users/", json={"email": "recipient_2@gmail.com", "name": "Recipient 2"}
    ).json()

    message = client.post(
        "/messages/",
        json={
            "sender_id": sender["id"],
            "recipient_ids": [recipient_1["id"], recipient_2["id"]],
            "subject": "Test Subject",
            "content": "Hello from test!",
        },
    ).json()

    return {
        "sender": sender,
        "recipients": [recipient_1, recipient_2],
        "message": message,
    }

# Send message
def test_send_message(test_data):
    message = test_data["message"]
    assert "id" in message


# Get sent
def test_get_sent_messages(test_data):
    sender_id = test_data["sender"]["id"]

    response = client.get(f"/messages/sent?user_id={sender_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Get inbox
def test_get_inbox(test_data):
    recipient_id = test_data["recipients"][0]["id"]

    inbox_list = client.get(f"/messages/inbox?user_id={recipient_id}")
    assert inbox_list.status_code == 200
    assert isinstance(inbox_list.json(), list)


# Get unread messages
def test_get_unread_messages(test_data):
    r_id = test_data["recipients"][0]["id"]
    unread = client.get(f"/messages/unread?user_id={r_id}")
    assert unread.status_code == 200
    assert isinstance(unread.json(), list)


# Get message with recipients (optional) 
def test_get_message_with_recipients(test_data):
    msg_id = test_data["message"]["id"]
    response = client.get(f"/messages/{msg_id}")
    assert response.status_code == 200
    assert "recipients" in response.json()

# Mark message as read
def test_mark_as_read(test_data):
    msg_id = test_data["message"]["id"]
    r_id = test_data["recipients"][0]["id"]
    response = client.post(f"/messages/{msg_id}/read?recipient_id={r_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "marked as read"
