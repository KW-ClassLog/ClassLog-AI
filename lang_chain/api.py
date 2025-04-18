from fastapi import FastAPI
from pydantic import BaseModel
from lang_chain.ocr import process_any_document
from lang_chain.whisper import transcribe_audio
from lang_chain.quiz_generator import generate_quiz_with_memory
from lang_chain.memory import QuizMemory
from dotenv import load_dotenv
import os
from lang_chain.pipeline import build_pipeline_with_memory


load_dotenv()


DOCUMENT_PATH = os.getenv("DOCUMENT_PATH")
AUDIO_PATH = os.getenv("AUDIO_PATH")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")
USE_AUDIO = os.getenv("USE_AUDIO", "False").lower() == "true"

app = FastAPI()
pipeline = build_pipeline_with_memory(DOCUMENT_PATH, AUDIO_PATH, USE_AUDIO, OPENROUTER_API_KEY, WHISPER_API_KEY)
regenerate_count = 0

class QuizResponse(BaseModel):
    quiz: str
    status: str

# 퀴즈 생성 API
@app.get("/generate-quiz", response_model=QuizResponse)
def generate_quiz():
    global regenerate_count
    regenerate_count = 0
    result = pipeline.invoke(None)
    return {"quiz": result, "status": "초기 퀴즈 생성 완료"}

# 퀴즈 재생성 API
@app.get("/regenerate-quiz", response_model=QuizResponse)
def regenerate_quiz():
    global regenerate_count
    if regenerate_count >= 1:
        return {"quiz": "", "status": "더 이상 퀴즈를 재생성할 수 없습니다."}
    regenerate_count += 1
    result = pipeline.invoke(None)
    return {"quiz": result, "status": f"재생성 퀴즈 {regenerate_count}회차 완료"}
