# app/main.py
from fastapi import FastAPI
from app.api.routes import session_init, survey_question
from app.services.db_connection import init_db_connection
from app.services.llm_client import init_llm_client

# Initialize DB connection and LLM client at startup
init_db_connection()
init_llm_client()

app = FastAPI(
    title="Intelligent Survey API",
    description="REST API for communicating with an LLM to generate health questionnaires as a decision tree.",
    version="0.1.0",
)

app.include_router(session_init.router)
app.include_router(survey_question.router)