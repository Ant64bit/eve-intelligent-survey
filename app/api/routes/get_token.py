# api/routes/get_token.py
from fastapi import APIRouter

router = APIRouter()
import uuid
# 3 routes

# une route pour récupérer un token de session

@router.post("/get_sessions_token", summary="Obtenir un token de session", tags=["Authentication"])
def get_token() -> dict:
    """
    Obtenir un token de session via uuid
    """
    token = str(uuid.uuid4())
    return {"token": token}


# une route pour obtenir l'humeur de l'utilisateur


# une route pour boucler sur le questionnaire