# api/routes/session_init.py

from fastapi import APIRouter
import uuid
from app.services.db_connection import get_db_connection

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/init", summary="Initialize a session")
def session_init() -> dict:
    """
    Creates a new session and returns the uuid token
    """
    token = str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (uuid) VALUES (%s)", (token,))
    conn.commit()
    cursor.close()
    conn.close()

    return {"token": token}