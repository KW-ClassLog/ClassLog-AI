from langchain.schema.runnable import RunnableLambda, RunnableParallel
from lang_chain.ocr import process_any_document
from lang_chain.whisper import transcribe_audio
from lang_chain.quiz_generator import generate_quiz
from lang_chain.memory import QuizMemory

quiz_memory = QuizMemory()

def build_pipeline_with_memory(document_path: str, audio_path: str, use_audio: bool, api_key: str, whisper_key: str):
    return (
        RunnableParallel({
            "document_text": RunnableLambda(lambda _: process_any_document(document_path)),
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
