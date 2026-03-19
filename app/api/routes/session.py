# api/routes/get_token.py
from fastapi import APIRouter
import uuid

router = APIRouter()

@router.post("/get_sessions_token", summary="Obtenir un token de session", tags=["Authentication"])
def get_token() -> dict:
    """
    Obtenir un token de session via uuid
    """
    token = str(uuid.uuid4())
    return {"token": token}
