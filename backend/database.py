import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection

# Database connection using environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_db")

_client: Optional[MongoClient] = None
_db = None

try:
    _client = MongoClient(DATABASE_URL)
    _db = _client[DATABASE_NAME]
except Exception as e:
    # Defer connection errors to runtime usage
    _client = None
    _db = None


def db():
    """Return the active database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Check DATABASE_URL/DATABASE_NAME env vars.")
    return _db


def get_collection(name: str) -> Collection:
    return db()[name]


def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a document with created_at/updated_at timestamps."""
    now = datetime.utcnow()
    payload = {**data, "created_at": now, "updated_at": now}
    col = get_collection(collection_name)
    result = col.insert_one(payload)
    payload["_id"] = str(result.inserted_id)
    return payload


def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    filter_dict = filter_dict or {}
    col = get_collection(collection_name)
    docs = col.find(filter_dict).sort("created_at", -1).limit(limit)
    out: List[Dict[str, Any]] = []
    for d in docs:
        d["_id"] = str(d.get("_id"))
        out.append(d)
    return out
