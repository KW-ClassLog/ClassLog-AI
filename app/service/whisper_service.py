import requests
from openai import OpenAI
from pydub import AudioSegment
from io import BytesIO

def transcribe_audio(file_path: str, chunk_sec: int = 300, api_key: str = "") -> str:

    print(f"오디오 파일 다운로드를 시작합니다: {file_path}", flush=True)
    try:
        response = requests.get(file_path, timeout=60)
        response.raise_for_status()
        print("오디오 파일 다운로드 완료.", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"오디오 파일 다운로드 중 오류 발생: {e}", flush=True)
        return "" 

    audio_file = BytesIO(response.content)
    audio = AudioSegment.from_file(audio_file)

    client = OpenAI(api_key=api_key, timeout=300.0)

    total_ms = len(audio)
    chunk_ms = chunk_sec * 1000
    full_text = ""

    total_chunks = (total_ms + chunk_ms - 1) // chunk_ms
    print(f"Whisper 전사를 시작합니다. (총 {total_chunks}개 조각)", flush=True)

    for idx, i in enumerate(range(0, total_ms, chunk_ms)):
        
        print(f" - [Whisper] {idx + 1}/{total_chunks}번째 조각 처리 중...", flush=True)
        
        chunk = audio[i:i + chunk_ms]

        try:
            with BytesIO() as buffer:
                chunk.export(buffer, format="mp3")
                buffer.seek(0)

                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("chunk.mp3", buffer, "audio/mpeg")
                )
                full_text += transcript.text.strip() + "\n\n"
                print(f"   - [Whisper] {idx + 1}/{total_chunks}번째 조각 처리 완료.", flush=True)

        except Exception as e:
            print(f"   - [Whisper] {idx + 1}/{total_chunks}번째 조각 처리 중 오류 발생: {e}", flush=True)
            
            continue

    print("Whisper 전사 작업이 모두 완료되었습니다.", flush=True)
    return full_text.strip()