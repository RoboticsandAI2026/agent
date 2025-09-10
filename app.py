# app.py
import os, sqlite3, time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

DB_PATH = "convos.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT CHECK(role IN ('user','assistant')),
            text TEXT,
            ts REAL
        )""")
init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Optional: set this on Render dashboard > Environment > INYA_SECRET
INYA_SECRET = os.getenv("INYA_SECRET", "")

class InyaEvent(BaseModel):
    session_id: str
    role: str            # "user" or "assistant"
    text: str
    ts: Optional[float]  # unix seconds (optional)

@app.post("/inya_webhook")
async def inya_webhook(request: Request, evt: InyaEvent):
    # (Optional) verify secret header
    if INYA_SECRET:
        if request.headers.get("X-Inya-Secret") != INYA_SECRET:
            raise HTTPException(status_code=401, detail="Bad secret")
    ts = evt.ts or time.time()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, text, ts) VALUES (?,?,?,?)",
            (evt.session_id, evt.role, evt.text, ts)
        )
    return {"ok": True}

@app.get("/conversations")
def conversations(session_id: Optional[str] = None, limit: int = 100):
    q = "SELECT session_id, role, text, ts FROM messages"
    params: List = []
    if session_id:
        q += " WHERE session_id=?"
        params.append(session_id)
    q += " ORDER BY ts DESC LIMIT ?"
    params.append(limit)
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(q, tuple(params)).fetchall()
    return [
        {"session_id": r[0], "role": r[1], "text": r[2], "ts": r[3]}
        for r in rows
    ]
