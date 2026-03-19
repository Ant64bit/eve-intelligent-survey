# app/main.py

from fastapi import FastAPI
from app.api.routes import session_init, survey_question, user_tone

app = FastAPI(
    title="Intelligent Survey API",
    description="API REST permettant de communiquer avec un LLM pour générer des questionnaires de santé sous forme d'arbre de décision.",
    version="0.1.0",
)

app.include_router(session_init.router)
app.include_router(user_tone.router)
app.include_router(survey_question.router)