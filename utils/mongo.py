# ...existing code...
import os
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, errors
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s]: %(message)s", level=logging.DEBUG)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "tucsfe_ai")

client: Optional[MongoClient] = None
db = None

def _init_client():
    global client, db
    if client is not None and db is not None:
        return
    try:
        logger.debug("Initializing MongoClient uri=%s db=%s", MONGO_URI, MONGO_DB)
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        client.admin.command("ping")
        logger.info("Connected to MongoDB (%s)", MONGO_DB)
    except errors.ServerSelectionTimeoutError as e:
        logger.exception("MongoDB unreachable: %s", e)
        client = None
        db = None
        raise
    except Exception as e:
        logger.exception("MongoDB init failed: %s", e)
        client = None
        db = None
        raise

# Password hashing
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    logger.debug("hash_password called")
    return pwd_ctx.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(password, hashed)
    except Exception:
        logger.exception("verify_password error")
        return False

def check_connection() -> bool:
    try:
        _init_client()
        if client is None:
            return False
        client.admin.command("ping")
        logger.debug("MongoDB ping OK")
        return True
    except Exception:
        logger.exception("check_connection failed")
        return False

# Users
def create_user(email: str, name: str, password: str, is_admin: bool = False) -> Dict[str, Any]:
    _init_client()
    try:
        logger.debug("create_user %s", email)
        if db.users.find_one({"email": email}):
            raise ValueError("User already exists")
        hashed = hash_password(password)
        user = {"email": email, "name": name, "password": hashed, "is_admin": is_admin, "created_at": datetime.utcnow()}
        res = db.users.insert_one(user)
        logger.info("create_user inserted id=%s", res.inserted_id)
        user.pop("password", None)
        return user
    except Exception:
        logger.exception("create_user failed")
        raise

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    _init_client()
    try:
        logger.debug("get_user_by_email %s", email)
        return db.users.find_one({"email": email})
    except Exception:
        logger.exception("get_user_by_email failed")
        return None

def list_users() -> List[Dict[str, Any]]:
    _init_client()
    try:
        logger.debug("list_users called")
        return list(db.users.find({}, {"password": 0}))
    except Exception:
        logger.exception("list_users failed")
        return []

# Sessions
def create_session(email: str, hours: int = 24) -> str:
    _init_client()
    try:
        token = str(uuid4())
        expires = datetime.utcnow() + timedelta(hours=hours)
        res = db.session.insert_one({"token": token, "email": email, "created_at": datetime.utcnow(), "expires": expires})
        logger.info("create_session for %s token=%s id=%s", email, token, res.inserted_id)
        return token
    except Exception:
        logger.exception("create_session failed")
        raise

def validate_session(token: str) -> Optional[str]:
    _init_client()
    try:
        logger.debug("validate_session %s", token)
        rec = db.session.find_one({"token": token})
        if not rec:
            return None
        if rec.get("expires") and rec["expires"] < datetime.utcnow():
            db.session.delete_one({"_id": rec["_id"]})
            return None
        return rec.get("email")
    except Exception:
        logger.exception("validate_session failed")
        return None

def delete_session(token: str) -> None:
    _init_client()
    try:
        res = db.session.delete_one({"token": token})
        logger.info("delete_session deleted=%s token=%s", res.deleted_count, token)
    except Exception:
        logger.exception("delete_session failed")
        raise

# Feedback & events
def add_feedback(email: str, query: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    _init_client()
    try:
        doc = {"email": email, "query": query, "response": response, "metadata": metadata or {}, "created_at": datetime.utcnow()}
        res = db.feedback.insert_one(doc)
        logger.info("add_feedback inserted id=%s for %s", res.inserted_id, email)
    except Exception:
        logger.exception("add_feedback failed")
        raise

def get_feedback(limit: int = 100) -> List[Dict[str, Any]]:
    _init_client()
    try:
        return list(db.feedback.find().sort("created_at", -1).limit(limit))
    except Exception:
        logger.exception("get_feedback failed")
        return []

def add_event(username: str, event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    _init_client()
    try:
        doc = {"username": username, "event_type": event_type, "details": details or {}, "timestamp": datetime.utcnow().isoformat()}
        res = db.session.insert_one(doc)
        logger.info("add_event inserted id=%s for %s", res.inserted_id, username)
    except Exception:
        logger.exception("add_event failed")
        raise
# ...existing code...