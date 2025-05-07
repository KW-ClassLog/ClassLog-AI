from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.quiz_api import quiz_router

load_dotenv()

app = FastAPI()

app.include_router(quiz_router)