from langchain.schema.runnable import RunnableLambda, RunnableParallel
from app.service.ocr_service import process_any_documents
from app.service.whisper_service import transcribe_audio

def build_pipeline_with_memory(document_path: str, audio_path: str | None, use_audio: bool, api_key: str):

    return RunnableParallel({
        "document_text": RunnableLambda(lambda _: process_any_documents(document_path)),
        "audio_text": RunnableLambda(lambda _: transcribe_audio(audio_path, api_key=api_key) if (use_audio and audio_path) else ""),
        "memory": RunnableLambda(lambda x: x["memory"]),
        "audio_present": RunnableLambda(lambda _: bool(use_audio and audio_path)),
    })