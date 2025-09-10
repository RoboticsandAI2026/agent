# app.py snippet
import os, sqlite3, time, json
from fastapi import FastAPI, Request, HTTPException

INYA_SECRET = os.getenv("INYA_SECRET", "")

@app.post("/inya_webhook")
async def inya_webhook(request: Request):
    # Auth
    if INYA_SECRET and request.headers.get("X-Inya-Secret") != INYA_SECRET:
        raise HTTPException(status_code=401, detail="Bad secret")

    payload = await request.json()
    print("INYA WEBHOOK PAYLOAD:", json.dumps(payload, ensure_ascii=False))

    # Flexible extraction of common field names
    sid = (
        payload.get("session_id")
        or payload.get("sessionId")
        or payload.get("conversation_id")
        or payload.get("conversationId")
        or (payload.get("session") or {}).get("id")
        or "unknown"
    )
    role = payload.get("role") or (
        "assistant" if str(payload.get("from","")).lower() in {"bot","assistant","ai"} else "user"
    )
    text = (
        payload.get("text")
        or payload.get("message")
        or (payload.get("output") or {}).get("message")
        or (payload.get("data") or {}).get("text")
    )
    ts = payload.get("ts") or time.time()

    if not text:
        raise HTTPException(status_code=400, detail="No text field found")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, text, ts) VALUES (?,?,?,?)",
            (sid, role, text, ts)
        )
    return {"ok": True}
