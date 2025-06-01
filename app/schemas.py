# Pydantic models
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


# Message schemas
class MessageCreate(BaseModel):
    sender_id: UUID
    subject: Optional[str]
    content: str
    recipient_ids: List[UUID]


class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    subject: Optional[str]
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True


class MessageRecipientResponse(BaseModel):
    id: UUID
    message_id: UUID
    recipient_id: UUID
    read: bool
    read_at: Optional[datetime]

    class Config:
        orm_mode = True


class MessageDetailResponse(BaseModel):
    id: UUID
    sender_id: UUID
    subject: Optional[str]
    content: str
    timestamp: datetime
    recipients: List[MessageRecipientResponse]

    class Config:
        orm_mode = True
