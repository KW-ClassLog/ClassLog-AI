from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from app.pipeline.pipeline import build_pipeline_with_memory
from app.core.memory import get_lecture_memory, lecture_memories
from app.service.vector_meta_service import VECTOR_DIR
from app.service.vector_store_service import (
    vectorstore_exists,
    save_vectorstore,
    load_vectorstore,
)
from app.service.quiz_generator_service import generate_quiz_with_rag
from app.utils.parse_utils import parse_quiz_output

from app.service.vector_meta_service import (
    get_has_audio,
    set_has_audio,
    write_meta,
)

router = APIRouter()

regenerate_count = {}


class QuizResponse(BaseModel):
    lecture_id: str
    quizzes: list[dict]

class QuizRequest(BaseModel):
    document_path: str
    use_audio: bool
    audio_path: str | None = None

# 퀴즈 생성 API
@router.post("/generate-quiz", response_model=QuizResponse)
def generate_quiz(lecture_id: str = Query(...), request: QuizRequest = Body(...)):

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    memory = get_lecture_memory(lecture_id)

    if not vectorstore_exists(lecture_id):

        out = build_pipeline_with_memory(
            document_path=request.document_path,
            audio_path=request.audio_path,
            use_audio=request.use_audio,
            api_key=OPENAI_API_KEY,
        ).invoke({"memory": memory})

        document_text = out["document_text"]
        audio_text = out["audio_text"]
        audio_present = bool(audio_text and audio_text.strip())

        combined = (document_text or "") + (("\n\n" + audio_text) if audio_text else "")
        save_vectorstore(lecture_id, combined, OPENAI_API_KEY)

        write_meta(lecture_id, {"has_audio": audio_present})

    else:
        audio_present = get_has_audio(lecture_id)

        if request.use_audio and request.audio_path and not audio_present:
            out = build_pipeline_with_memory(
                document_path = "",
                audio_path = request.audio_path,
                use_audio = True,
                api_key = OPENAI_API_KEY,
            ).invoke({"memory": memory})

            audio_text = out["audio_text"] or ""
            if audio_text.strip():
                vs = load_vectorstore(lecture_id, OPENAI_API_KEY)
                chunks = [c for c in audio_text.split("\n\n") if c.strip()]
                if chunks:
                    vs.add_texts(texts = chunks, metadatas = [{"source": "audio"} for _ in chunks])
                    vs.save_local(os.path.join(VECTOR_DIR, lecture_id))
                    set_has_audio(lecture_id, True)
                    audio_present = True

    quiz_text = generate_quiz_with_rag(
        lecture_id = lecture_id,
        memory = memory,
        api_key = OPENAI_API_KEY,
        model = "gpt-4o",
        audio_present = audio_present,
    )

    memory.add(quiz_text)

    quizzes = parse_quiz_output(quiz_text)
    return QuizResponse(lecture_id = lecture_id, quizzes = quizzes)


# 퀴즈 재생성
@router.post("/regenerate-quiz", response_model = QuizResponse)
def regenerate_quiz(lecture_id: str = Query(...), request: QuizRequest = Body(...)):

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 재생성 1회 제한
    count = regenerate_count.get(lecture_id, 0)
    if count >= 1:
        return QuizResponse(lecture_id=lecture_id, quizzes=[])

    memory = get_lecture_memory(lecture_id)

    if not vectorstore_exists(lecture_id):

        out = build_pipeline_with_memory(
            document_path=request.document_path,
            audio_path=request.audio_path,
            use_audio=request.use_audio,
            api_key=OPENAI_API_KEY,
        ).invoke({"memory": memory})

        document_text = out["document_text"]
        audio_text = out["audio_text"]
        audio_present = bool(audio_text and audio_text.strip())

        combined = (document_text or "") + (("\n\n" + audio_text) if audio_text else "")
        save_vectorstore(lecture_id, combined, OPENAI_API_KEY)

        set_has_audio(lecture_id, audio_present)

    else:
        
        audio_present = get_has_audio(lecture_id)
        

        if request.use_audio and request.audio_path and not audio_present:
            out = build_pipeline_with_memory(
                document_path="",
                audio_path=request.audio_path,
                use_audio=True,
                api_key=OPENAI_API_KEY,
            ).invoke({"memory": memory})

            audio_text = out["audio_text"] or ""
            if audio_text.strip():
                vs = load_vectorstore(lecture_id, OPENAI_API_KEY)
                chunks = [c for c in audio_text.split("\n\n") if c.strip()]
                if chunks:
                    vs.add_texts(
                        texts=chunks,
                        metadatas=[{"source": "audio"} for _ in chunks]
                    )
                    vs.save_local(os.path.join(VECTOR_DIR, lecture_id))
                    set_has_audio(lecture_id, True)
                    audio_present = True

    
    quiz_text = generate_quiz_with_rag(
        lecture_id=lecture_id,
        memory=memory,
        api_key=OPENAI_API_KEY,
        model="gpt-4o",
        audio_present = audio_present,
    )

    quizzes = parse_quiz_output(quiz_text)

    regenerate_count[lecture_id] = count + 1

    if lecture_id in lecture_memories:
        del lecture_memories[lecture_id]

    return QuizResponse(lecture_id=lecture_id, quizzes=quizzes)


# 강의별 퀴즈 메모리 확인 API(test용)
@router.get("/quiz-history")
def get_quiz_history(lecture_id: str = Query(...)):
    memory = lecture_memories.get(lecture_id)
    if not memory:
        return JSONResponse(content={"message": "해당 lecture_id에 대한 퀴즈 이력이 없습니다."}, status_code=404)
    
    return {
        "lecture_id": lecture_id,
        "history_count": len(memory.get_all()),
        "history": memory.get_all()
    }