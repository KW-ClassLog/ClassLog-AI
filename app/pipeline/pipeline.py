from langchain.schema.runnable import RunnableLambda, RunnableParallel
from app.service.ocr_service import process_any_documents
from app.service.whisper_service import transcribe_audio
from app.service.quiz_generator_service import generate_quiz
from app.core.memory import QuizMemory

quiz_memory = QuizMemory()

def build_pipeline_with_memory(document_path: str, audio_path: str, use_audio: bool, api_key: str, whisper_key: str):
    return (
        RunnableParallel({
            "document_text": RunnableLambda(lambda _: process_any_documents(document_path)),
            "audio_text": RunnableLambda(lambda _: transcribe_audio(audio_path, api_key=whisper_key) if use_audio else ""),
            "memory": RunnableLambda(lambda x: x["memory"]),
        })
        | RunnableLambda(lambda inputs: generate_quiz(
            document_text=inputs["document_text"],
            audio_text=inputs["audio_text"],
            memory=inputs["memory"],
            api_key=api_key
        ))
    )