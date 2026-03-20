# app/main.py
from fastapi import FastAPI
from app.api.routes import session_init, survey_question, user_tone
from app.services.db_connection import init_connection

init_connection()

app = FastAPI(
    title="Intelligent Survey API",
    description="REST API for communicating with an LLM to generate health questionnaires as a decision tree.",
    version="0.1.0",
)

app.include_router(session_init.router)
app.include_router(user_tone.router)
app.include_router(survey_question.router)