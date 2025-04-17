from fastapi import FastAPI
from pydantic import BaseModel
from lang_chain.ocr import process_any_document
from lang_chain.whisper import transcribe_audio
from lang_chain.quiz_generator import generate_quiz_with_memory
from lang_chain.memory import QuizMemory
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")
DOCUMENT_PATH = "test_input/TM_5.2._Topic_Modeling(2)_2024.pdf"
AUDIO_PATH = ""
USE_AUDIO = False

app = FastAPI()
quiz_memory = QuizMemory()
document_text = process_any_document(DOCUMENT_PATH)
audio_text = transcribe_audio(AUDIO_PATH, api_key=WHISPER_API_KEY) if USE_AUDIO else ""
regenerate_count = 0

class QuizResponse(BaseModel):
    quiz: str
    status: str

    # 퀴즈 생성 API
    @app.get("/generate-quiz", response_model=QuizResponse)
    def generate_quiz():
        global regenerate_count
        regenerate_count = 0
        quiz = generate_quiz_with_memory(document_text, audio_text, quiz_memory, OPENROUTER_API_KEY)
        return {"quiz": quiz, "status": "초기 퀴즈 생성 완료"}

    # 퀴즈 재생성 API
    @app.get("/regenerate-quiz", response_model=QuizResponse)
    def regenerate_quiz():
        global regenerate_count
        if regenerate_count >= 1:
            return {"quiz": "", "status": "더 이상 퀴즈를 재생성할 수 없습니다."}

        regenerate_count += 1
        quiz = generate_quiz_with_memory(document_text, audio_text, quiz_memory, OPENROUTER_API_KEY)
        return {"quiz": quiz, "status": f"재생성 퀴즈 {regenerate_count}회차 완료"}
