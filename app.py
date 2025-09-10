# app.py (FastAPI)
import os, sqlite3, time
from fastapi import FastAPI, Request, HTTPException

INYA_SECRET = os.getenv("X-Inya-Secret", "")

@app.post("/inya_webhook")
async def inya_webhook(request: Request, evt: InyaEvent):
    # ✅ Authentication check goes here
    if INYA_SECRET:
        incoming = request.headers.get("X-Inya-Secret", "")
        if incoming != INYA_SECRET:
            raise HTTPException(status_code=401, detail="Bad secret")

    ts = evt.ts or time.time()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, text, ts) VALUES (?,?,?,?)",
            (evt.session_id, evt.role, evt.text, ts)
        )
    return {"ok": True}
