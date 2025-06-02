# Optional MCP server logic
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.routes import get_db
from app import models

app = FastAPI(title="Messaging MCP Server")


# --- MCP Models ---
class MCPRequest(BaseModel):
    input: Optional[str] = None  # text prompt
    params: Optional[dict] = None  
    context: Optional[dict] = None  

class MCPResponse(BaseModel):
    output: Optional[str] = None
    data: Optional[dict] = None  
    context: Optional[dict] = None

# MCP: Create a user
@app.post("/mcp/create_user", response_model=MCPResponse)
def create_user_tool(req: MCPRequest, db: Session = Depends(get_db)):
    params = req.params or {}
    email = params.get("email")
    name = params.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Missing 'email' or 'name'")
    # Check duplicate email
    if db.query(models.User).filter(models.User.email == email).first():
        return MCPResponse(output=f"Email {email} already exists.", context=req.context)
    user = models.User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return MCPResponse(
        output=f"User {name} created with ID {user.id}",
        data={"user_id": str(user.id), "email": user.email, "name": user.name},
        context=req.context,
    )

# MCP: List users
@app.post("/mcp/list_users", response_model=MCPResponse)
def list_users_tool(req: MCPRequest, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    users_list = [{"id": str(u.id), "email": u.email, "name": u.name} for u in users]
    return MCPResponse(
        output=f"Found {len(users_list)} users.",
        data={"users": users_list},
        context=req.context,
    )

# MCP: Send message
@app.post("/mcp/send_message", response_model=MCPResponse)
def send_message_tool(req: MCPRequest, db: Session = Depends(get_db)):
    params = req.params or {}
    sender_id = params.get("sender_id")
    subject = params.get("subject")
    content = params.get("content")
    recipient_ids = params.get("recipient_ids", [])
    if not sender_id or not content or not recipient_ids:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: 'sender_id', 'content', 'recipient_ids'",
        )
    # Check sender exists
    sender = db.query(models.User).filter(models.User.id == sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    msg = models.Message(sender_id=sender_id, subject=subject, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    for rid in recipient_ids:
        recipient = db.query(models.User).filter(models.User.id == rid).first()
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Recipient {rid} not found")
        mr = models.MessageRecipient(message_id=msg.id, recipient_id=rid, read=False)
        db.add(mr)
    db.commit()

    return MCPResponse(
        output=f"Message sent with ID {msg.id}",
        data={"message_id": str(msg.id)},
        context=req.context,
    )

# MCP: Inbox messages
@app.post("/mcp/inbox", response_model=MCPResponse)
def inbox_tool(req: MCPRequest, db: Session = Depends(get_db)):
    params = req.params or {}
    user_id = params.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing 'user_id'")
    messages = (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(models.MessageRecipient.recipient_id == user_id)
        .all()
    )
    messages_data = []
    for m in messages:
        messages_data.append(
            {
                "id": str(m.id),
                "sender_id": str(m.sender_id),
                "subject": m.subject,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
        )
    return MCPResponse(
        output=f"Found {len(messages_data)} messages in inbox.",
        data={"messages": messages_data},
        context=req.context,
    )

# MCP: Mark message as read
@app.post("/mcp/mark_read", response_model=MCPResponse)
def mark_read_tool(req: MCPRequest, db: Session = Depends(get_db)):
    params = req.params or {}
    message_id = params.get("message_id")
    recipient_id = params.get("recipient_id")
    if not message_id or not recipient_id:
        raise HTTPException(
            status_code=400, detail="Missing 'message_id' or 'recipient_id'"
        )
    mr = (
        db.query(models.MessageRecipient)
        .filter(
            models.MessageRecipient.message_id == message_id,
            models.MessageRecipient.recipient_id == recipient_id,
        )
        .first()
    )
    if not mr:
        raise HTTPException(status_code=404, detail="Recipient not found for this message")
    mr.read = True
    mr.read_at = datetime.utcnow()
    db.commit()
    return MCPResponse(output="Marked as read", context=req.context)
