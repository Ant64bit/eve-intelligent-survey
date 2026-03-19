# api/routes/session_init.py

from fastapi import APIRouter
import uuid
from app.services.db_connection import get_db_connection

router = APIRouter()

@router.post("/session/init", summary="Initialiser une session", tags=["Session"])
def session_init() -> dict:
    """
    Crée une nouvelle session et retourne le token uuid
    """
    token = str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (uuid) VALUES (%s)", (token,))
    conn.commit()
    cursor.close()
    conn.close()

    return {"token": token}