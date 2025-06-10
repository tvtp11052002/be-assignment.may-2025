# Optional MCP server logic
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastmcp import FastMCP
from sqlalchemy.orm import joinedload

from app import models, schemas
from app.db import get_db, get_db_session
from app.models import Message, MessageRecipient, User

# Initialize MCP server
mcp = FastMCP("Messaging System")


def serialize_user(user: User):
    """Serialize User object to dictionary"""
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
    }


def serialize_message(message: Message):
    """Serialize Message object to dictionary"""
    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "subject": message.subject,
        "content": message.content,
        "timestamp": message.timestamp,
    }


def serialize_message_with_recipients(message: MessageRecipient):
    """Serialize Message recipients to dictionary"""
    result = serialize_message(message)
    result["recipients"] = [
        {"recipient_id": str(mr.recipient_id), "read": mr.read, "read_at": mr.read_at}
        for mr in message.recipients
    ]
    return result


#### USER TOOLS ####


@mcp.tool()
def create_user(email: str, name: str):
    """Create a new user"""
    db = get_db_session()
    try:
        db_user = models.User(email=email, name=name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return serialize_user(db_user)
    finally:
        db.close()


@mcp.tool()
def list_users():
    """List all users"""
    db = get_db_session()
    try:
        users = db.query(models.User).all()
        return [serialize_user(user) for user in users]
    finally:
        db.close()


@mcp.tool()
def get_user(user_id: str):
    """Retrieve user information"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("Invalid user ID format")

    db = get_db_session()
    try:
        user = db.query(models.User).filter(models.User.id == user_uuid).first()
        if not user:
            raise ValueError("User not found")
        return serialize_user(user)
    finally:
        db.close()


@mcp.tool()
def delete_all_users():
    """Delete all users"""
    db = get_db_session()
    try:
        db.query(models.User).delete()
        db.commit()
        return {"detail": "All users deleted"}
    finally:
        db.close()


#### MESSAGE TOOLS ####


@mcp.tool()
def send_message(sender_id: str, recipient_ids: List[str], subject: str, content: str):
    """Send a message"""
    try:
        sender_uuid = UUID(sender_id)
        recipient_uuids = [UUID(rid) for rid in recipient_ids]
    except ValueError:
        raise ValueError("Invalid UUID format in sender_id or recipient_ids")

    db = get_db_session()
    try:
        sender = db.query(User).filter(User.id == sender_uuid).first()
        if not sender:
            raise ValueError("Sender not found")

        msg = Message(sender_id=sender_uuid, subject=subject, content=content)
        db.add(msg)
        db.flush()

        for rid in recipient_uuids:
            recipient = db.query(User).filter(User.id == rid).first()
            if not recipient:
                raise ValueError(f"Recipient {rid} not found")

            mr = MessageRecipient(message_id=msg.id, recipient_id=rid, read=False)
            db.add(mr)

        db.commit()
        db.refresh(msg)
        return serialize_message(msg)
    finally:
        db.close()


@mcp.tool()
def get_sent_messages(user_id: str):
    """Get sent messages"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("Invalid user ID format")

    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise ValueError("User not found")

        messages = db.query(Message).filter(Message.sender_id == user_uuid).all()
        return [serialize_message(msg) for msg in messages]
    finally:
        db.close()


@mcp.tool()
def get_inbox(user_id: str):
    """View inbox messages"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("Invalid user ID format")

    db = get_db_session()
    try:
        messages = (
            db.query(Message)
            .join(MessageRecipient)
            .filter(MessageRecipient.recipient_id == user_uuid)
            .all()
        )
        return [serialize_message(msg) for msg in messages]
    finally:
        db.close()


@mcp.tool()
def get_unread_messages(user_id: str):
    """View unread messages"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("Invalid user ID format")

    db = get_db_session()
    try:
        messages = (
            db.query(Message)
            .join(MessageRecipient)
            .filter(
                MessageRecipient.recipient_id == user_uuid,
                MessageRecipient.read == False,
            )
            .all()
        )
        return [serialize_message(msg) for msg in messages]
    finally:
        db.close()


@mcp.tool()
def get_message_with_recipients(message_id: str):
    """View recipients message"""
    try:
        message_uuid = UUID(message_id)
    except ValueError:
        raise ValueError("Invalid message ID format")

    db = get_db_session()
    try:
        msg = (
            db.query(Message)
            .options(joinedload(Message.recipients))
            .filter(Message.id == message_uuid)
            .first()
        )
        if not msg:
            raise ValueError("Message not found")

        return serialize_message_with_recipients(msg)
    finally:
        db.close()


@mcp.tool()
def mark_message_as_read(message_id: str, recipient_id: str):
    """Mark a message as read"""
    try:
        message_uuid = UUID(message_id)
        recipient_uuid = UUID(recipient_id)
    except ValueError:
        raise ValueError("Invalid UUID format")

    db = get_db_session()
    try:
        mr = (
            db.query(MessageRecipient)
            .filter(
                MessageRecipient.message_id == message_uuid,
                MessageRecipient.recipient_id == recipient_uuid,
            )
            .first()
        )
        if not mr:
            raise ValueError("Recipient not found for this message")

        mr.read = True
        mr.read_at = datetime.utcnow()
        db.commit()

        return {"status": "marked as read"}
    finally:
        db.close()


#### RESOURCE HANDLERS ####


@mcp.resource("messaging://users")
def get_all_users_resource():
    """Resource handler for all users"""
    users = list_users()
    return json.dumps(users, indent=2)


@mcp.resource("messaging://users/{user_id}")
def get_user_resource(user_id: str):
    """Resource handler for specific user"""
    user = get_user(user_id)
    return json.dumps(user, indent=2)


@mcp.resource("messaging://messages/inbox/{user_id}")
def get_inbox_resource(user_id: str):
    """Resource handler for user's inbox"""
    messages = get_inbox(user_id)
    return json.dumps(messages, indent=2)


@mcp.resource("messaging://messages/sent/{user_id}")
def get_sent_messages_resource(user_id: str):
    """Resource handler for user's sent messages"""
    messages = get_sent_messages(user_id)
    return json.dumps(messages, indent=2)


@mcp.resource("messaging://messages/unread/{user_id}")
def get_unread_messages_resource(user_id: str):
    """Resource handler for user's unread messages"""
    messages = get_unread_messages(user_id)
    return json.dumps(messages, indent=2)


@mcp.resource("messaging://messages/{message_id}")
def get_message_resource(message_id: str):
    """Resource handler for specific message with recipients"""
    message = get_message_with_recipients(message_id)
    return json.dumps(message, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
