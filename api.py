from fastapi import FastAPI, Request, HTTPException, Depends, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging
import os
from utils.mongo import create_session, validate_session, add_feedback, add_event
from rag_pipeline import ask_with_rag

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s]: %(message)s", level=logging.DEBUG)

app = FastAPI()

FRONTEND_ORIGINS = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class TokenIn(BaseModel):
    id_token: str

class AskIn(BaseModel):
    prompt: str

def verify_google_id_token(id_token: str):
    r = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}, timeout=5)
    if r.status_code != 200:
        logger.warning("tokeninfo failed %s %s", r.status_code, r.text)
        raise HTTPException(status_code=401, detail="Invalid Google token")
    info = r.json()
    if GOOGLE_CLIENT_ID and info.get("aud") != GOOGLE_CLIENT_ID:
        logger.warning("aud mismatch %s", info.get("aud"))
        raise HTTPException(status_code=401, detail="Invalid token audience")
    return {"email": info.get("email"), "name": info.get("name")}

def get_current_user(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Missing session token")
    email = validate_session(session_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return email

@app.post("/api/login")
def login(token: TokenIn, response: Response):
    info = verify_google_id_token(token.id_token)
    email = info["email"]
    sess = create_session(email, hours=24)
    response.set_cookie(key="session_token", value=sess, httponly=True, samesite="lax")
    add_event(email, "login", {"via": "google"})
    logger.info("login success %s", email)
    return {"email": email, "name": info.get("name")}

@app.post("/api/ask")
def ask_item(req: AskIn, user_email: str = Depends(get_current_user)):
    logger.info("ask request by %s prompt_len=%d", user_email, len(req.prompt))
    try:
        response_text = ask_with_rag(req.prompt)
    except Exception:
        logger.exception("RAG error")
        raise HTTPException(status_code=500, detail="RAG error")
    try:
        add_feedback(user_email, req.prompt, response_text, metadata={"source": "ui"})
        add_event(user_email, "query", {"prompt_len": len(req.prompt)})
    except Exception:
        logger.exception("persist feedback failed")
    return {"response": response_text}

@app.post("/api/logout")
def logout(response: Response, session_token: str = Cookie(None)):
    if session_token:
        from utils.mongo import delete_session
        try:
            delete_session(session_token)
        except Exception:
            logger.exception("delete_session failed")
    response.delete_cookie("session_token")
    return {"ok": True}