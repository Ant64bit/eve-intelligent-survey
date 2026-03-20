# app/services/db_connection.py
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

conn = None

def init_connection():
    global conn
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT")
            )
            print("DB connectée ✅")
            return
        except Exception as e:
            retries -= 1
            print(f"DB pas prête, retry... ({retries} restants)")
            time.sleep(2)
    raise Exception("Impossible de se connecter à la DB")

def get_db_connection():
    return conn