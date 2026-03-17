# app/main.py
from fastapi import FastAPI
from app.api.routes import get_token

app = FastAPI(
    title="Intelligent Survey API",
    description="API REST permettant de communiquer avec un LLM pour générer des questionnaires de santé sous forme d'arbre de décision.",
    version="0.1.0",
)

app.include_router(get_token.router)