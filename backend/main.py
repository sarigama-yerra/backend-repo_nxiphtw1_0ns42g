from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from database import create_document, get_documents, db
import os

app = FastAPI(title="Portfolio API", version="1.0.0")

# CORS: allow the Vite dev server and any provided frontend URL
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessageIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)


class ContactMessageOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    message: str


@app.get("/test")
async def test():
    # Verify DB connectivity
    try:
        _ = db().list_collection_names()
        return {"ok": True, "database": "connected"}
    except Exception as e:
        return {"ok": False, "database": f"error: {e}"}


@app.post("/contact", response_model=ContactMessageOut)
async def contact_submit(payload: ContactMessageIn):
    try:
        saved = create_document(
            "message",
            {
                "name": payload.name.strip(),
                "email": str(payload.email).lower(),
                "message": payload.message.strip(),
                "source": "portfolio",
            },
        )
        return {
            "id": saved.get("_id"),
            "name": saved.get("name"),
            "email": saved.get("email"),
            "message": saved.get("message"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {e}")


@app.get("/messages")
async def list_messages(limit: int = 25):
    try:
        docs = get_documents("message", {}, limit=limit)
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
