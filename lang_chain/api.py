from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from dotenv import load_dotenv
from lang_chain.pipeline import build_pipeline_with_memory
from lang_chain.quiz_generator import parse_quiz_output
from lang_chain.memory import get_lecture_memory
from fastapi.responses import JSONResponse
from lang_chain.memory import lecture_memories
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")

app = FastAPI()
regenerate_count = {}

class QuizResponse(BaseModel):
    quizzes: list[dict]
    status: str

class QuizRequest(BaseModel):
    document_path: str
    use_audio: bool
    audio_path: str | None = None

# 퀴즈 생성 API
@app.post("/generate-quiz", response_model=QuizResponse)
def generate_quiz(
    lecture_id: str = Query(...),
    request: QuizRequest = Body(...)
):    
    regenerate_count[lecture_id] = 0

    pipeline = build_pipeline_with_memory(
        request.document_path,
        request.audio_path if request.use_audio else None,
        request.use_audio,
        OPENROUTER_API_KEY,
        WHISPER_API_KEY
    )

    memory = get_lecture_memory(lecture_id)
    raw_text = pipeline.invoke({"memory": memory})
    parsed = parse_quiz_output(raw_text)
    memory.add(raw_text)
    return {"quizzes": parsed, "status": "초기 퀴즈 생성 완료"}

# 퀴즈 재생성 API
@app.post("/regenerate-quiz", response_model=QuizResponse)
def regenerate_quiz(
    lecture_id: str = Query(...),
    request: QuizRequest = Body(...)
):    
    count = regenerate_count.get(lecture_id, 0)
    if count >= 1:
        return {"quizzes": [], "status": "더 이상 퀴즈를 재생성할 수 없습니다."}
    
    regenerate_count[lecture_id] = count + 1

    pipeline = build_pipeline_with_memory(
        request.document_path,
        request.audio_path if request.use_audio else None,
        request.use_audio,
        OPENROUTER_API_KEY,
        WHISPER_API_KEY
    )

    memory = get_lecture_memory(lecture_id)
    raw_text = pipeline.invoke({"memory": memory})
    parsed = parse_quiz_output(raw_text)
    return {"quizzes": parsed, "status": f"재생성 퀴즈 {regenerate_count[lecture_id]}회차 완료"}

# 메모리 초기화
@app.post("/reset-quiz-memory")
def reset_quiz_memory(lecture_id: str = Query(...)):
    if lecture_id in lecture_memories:
        del lecture_memories[lecture_id]
        return {"message": f"{lecture_id}의 퀴즈 메모리를 초기화했습니다."}
    return {"message": f"{lecture_id}에 해당하는 메모리가 없습니다."}

# 퀴즈 저장 메모리 확인(test용)
@app.get("/quiz-history")
def get_quiz_history(lecture_id: str = Query(...)):
    memory = lecture_memories.get(lecture_id)
    if not memory:
        return JSONResponse(content={"message": "해당 lecture_id에 대한 퀴즈 이력이 없습니다."}, status_code=404)

    return {
        "lecture_id": lecture_id,
        "history_count": len(memory.get_all()),
        "history": memory.get_all()
    }
