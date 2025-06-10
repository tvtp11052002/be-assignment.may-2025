# FastAPI routes
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.db import get_db
from app.models import Message, MessageRecipient, User

router = APIRouter()


#### Users APIs ####
# Create a user
@router.post(
    "/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# List users
@router.get("/users/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# Retrieve user info
@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Optional: Delete all users
@router.delete("/users/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_users(db: Session = Depends(get_db)):
    db.query(models.User).delete()
    db.commit()
    return {"detail": "All users deleted"}


#### Messages APIs ####
# Send a message to one or more recipients
@router.post(
    "/messages/",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(data: schemas.MessageCreate, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == data.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    msg = Message(sender_id=data.sender_id, subject=data.subject, content=data.content)
    db.add(msg)
    db.flush()

    for rid in data.recipient_ids:
        recipient = db.query(User).filter(User.id == rid).first()
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Recipient {rid} not found")
        mr = MessageRecipient(message_id=msg.id, recipient_id=rid, read=False)
        db.add(mr)

    db.commit()
    db.refresh(msg)
    return msg


# View sent messages
@router.get("/messages/sent", response_model=List[schemas.MessageResponse])
def get_sent_messages(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    messages = db.query(Message).filter(Message.sender_id == user_id).all()
    return messages


# View inbox messages
@router.get("/messages/inbox", response_model=List[schemas.MessageResponse])
def get_inbox(user_id: UUID, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .join(MessageRecipient)
        .filter(MessageRecipient.recipient_id == user_id)
        .all()
    )
    return messages


# View unread messages
@router.get("/messages/unread", response_model=List[schemas.MessageResponse])
def get_unread_messages(user_id: UUID, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .join(MessageRecipient)
        .filter(
            MessageRecipient.recipient_id == user_id, MessageRecipient.read == False
        )
        .all()
    )
    return messages


# View a message with all recipients
@router.get("/messages/{message_id}", response_model=schemas.MessageDetailResponse)
def get_message_with_recipients(message_id: UUID, db: Session = Depends(get_db)):
    msg = (
        db.query(Message)
        .options(joinedload(Message.recipients))
        .filter(Message.id == message_id)
        .first()
    )
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


# Mark a message as read (for a specific recipient)
@router.post("/messages/{message_id}/read")
def mark_as_read(message_id: UUID, recipient_id: UUID, db: Session = Depends(get_db)):
    mr = (
        db.query(MessageRecipient)
        .filter(
            MessageRecipient.message_id == message_id,
            MessageRecipient.recipient_id == recipient_id,
        )
        .first()
    )
    if not mr:
        raise HTTPException(
            status_code=404, detail="Recipient not found for this message"
        )
    mr.read = True
    mr.read_at = datetime.utcnow()
    db.commit()
    return {"status": "marked as read"}
