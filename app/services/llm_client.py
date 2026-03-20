# app/services/llm_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

llm_client = None

def init_llm_client():
    global llm_client
    try:
        llm_client = OpenAI(
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY")
        )
        print("LLM client initialisé ✅")
    except Exception as e:
        raise Exception(f"Impossible d'initialiser le client LLM : {e}")

def get_llm_client():
    return llm_client

if __name__ == "__main__":
    init_llm_client()
    client = get_llm_client()
    
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {"role": "system", "content": "Tu es un expert ostéopathe français. Sous aucun prétexte tu ne dois répondre dans une autre langue que le français."},
            {"role": "user", "content": "Dis moi bonjour en une phrase."}
        ]
    )
    
    print(response.choices[0].message.content)