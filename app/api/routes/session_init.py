# app/api/routes/session_init.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.db_connection import get_db_connection
from app.services.llm_client import get_llm_client
import os

router = APIRouter(prefix="/session", tags=["Session"])

class SessionInitRequest(BaseModel):
    uuid: str
    question_1: str
    reponse_q1: str
    question_2: str
    reponse_q2: str

@router.post("/init", summary="Initialize a session")
def session_init(body: SessionInitRequest) -> dict:
    
    # 1. Analyser le ton via le LLM
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {"role": "system", "content": """Tu es un expert en analyse linguistique. 
            Analyse le ton de l'utilisateur à partir de ses réponses.
            Retourne uniquement une ligne de résumé, sans introduction, sans bullet points, sans explication.
            Format attendu : [familiarité], [registre], [style], [vocabulaire]
            Exemple : Tutoiement, registre familier, style court et direct, vocabulaire simple
            Si l'utilisateur utilise un langage inapproprié ou des injures, ramène le ton à un registre neutre et poli."""},
            {"role": "user", "content": f"Question 1: {body.question_1}\nRéponse: {body.reponse_q1}\n\nQuestion 2: {body.question_2}\nRéponse: {body.reponse_q2}"}
        ]
    )
    ton = response.choices[0].message.content

    # 2. Créer l'entrée en base
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (uuid, ton) VALUES (%s, %s)",
        (body.uuid, ton)
    )
    conn.commit()
    cursor.close()

    # 3. TODO : appeler get_next_question() et retourner la première question
    return {"status": "ok", "ton": ton}