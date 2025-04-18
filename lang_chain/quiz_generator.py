import requests
from lang_chain.memory import QuizMemory

# 퀴즈 생성 + 메모리 저장 함수
def generate_quiz_with_memory(document_text: str, audio_text: str, memory: QuizMemory, api_key: str, model="deepseek/deepseek-chat") -> str:
    prompt = memory.get_prompt(document_text, audio_text)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()["choices"][0]["message"]["content"]
    memory.add(result)
    return result