from openai import OpenAI
from pydub import AudioSegment
from io import BytesIO
from tqdm import tqdm

# 강의 녹음 텍스트 변환 함수
def transcribe_audio(file_path: str, chunk_sec: int = 300, api_key: str = "") -> str:
    client = OpenAI(api_key=api_key)
    audio = AudioSegment.from_file(file_path)
    total_ms = len(audio)
    chunk_ms = chunk_sec * 1000
    full_text = ""

    for i in tqdm(range(0, total_ms, chunk_ms), desc="Whisper 전사 중"):
        chunk = audio[i:i + chunk_ms]
        buffer = BytesIO()
        chunk.export(buffer, format="mp3")
        buffer.seek(0)

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("chunk.mp3", buffer, "audio/mpeg")
        )
        full_text += transcript.text.strip() + "\n\n"

    return full_text.strip()