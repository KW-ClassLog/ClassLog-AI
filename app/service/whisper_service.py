import requests
from openai import OpenAI
from pydub import AudioSegment
from io import BytesIO
from tqdm import tqdm

# 강의 녹음 텍스트 변환 함수
def transcribe_audio(file_path: str, chunk_sec: int = 300, api_key: str = "") -> str:
    response = requests.get(file_path)
    response.raise_for_status()

    audio_file = BytesIO(response.content)
    audio = AudioSegment.from_file(audio_file)

    client = OpenAI(api_key=api_key)

    total_ms = len(audio)
    chunk_ms = chunk_sec * 1000
    full_text = ""

    for i in tqdm(range(0, total_ms, chunk_ms), desc="Whisper 전사 중"):
        chunk = audio[i:i + chunk_ms]

        with BytesIO() as buffer:
            chunk.export(buffer, format="mp3")
            buffer.seek(0)

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=("chunk.mp3", buffer, "audio/mpeg")
            )
            full_text += transcript.text.strip() + "\n\n"

    return full_text.strip()