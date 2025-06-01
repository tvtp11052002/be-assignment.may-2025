# Entry point for FastAPI app
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.db import Base, engine
from app.routes import router

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Messaging API running!"}
