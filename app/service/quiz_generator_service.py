from app.core.memory import QuizMemory
import requests

# 퀴즈 생성 함수
def generate_quiz(document_text: str, audio_text: str, memory: QuizMemory, api_key: str, model="gpt-4o") -> str:
    prompt = memory.get_prompt(document_text, audio_text)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()["choices"][0]["message"]["content"]

    # deepseek 퀴즈 응답 터미널에 출력
    print("===== 퀴즈 응답 =====")
    print(result)
    
    return result