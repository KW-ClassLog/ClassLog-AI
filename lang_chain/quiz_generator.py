import requests
from lang_chain.memory import QuizMemory
import re


# 퀴즈 생성 함수
def generate_quiz(document_text: str, audio_text: str, memory: QuizMemory, api_key: str, model="deepseek/deepseek-chat-v3-0324:free") -> str:
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

    # deepseek 퀴즈 응답 터미널에 출력
    print("===== 퀴즈 응답 =====")
    print(result)
    
    return result

# response 구조 변환 함수
def parse_quiz_output(raw_text: str) -> list[dict]:
    quizzes = []
    blocks = re.split(r"\[문항 유형: (.*?)\]", raw_text.strip())

    for i in range(1, len(blocks), 2):
        qtype_raw = blocks[i].strip()
        content = blocks[i + 1].strip()

        # 문제
        body_match = re.search(r"문제:\s*(.+)", content)
        body = body_match.group(1).strip() if body_match else "질문 없음"

        # 정답
        sol_match = re.search(r"정답:\s*(.+)", content)
        solution_raw = sol_match.group(1).strip() if sol_match else "정답 없음"

        # 보기
        choices = []
        if "객관식" in qtype_raw:
            choice_lines = re.findall(r"^\d\.\s+.+", content, re.MULTILINE)
            choices = [re.sub(r"^\d\.\s*", "", line).strip() for line in choice_lines]

            if solution_raw.isdigit():
                idx = int(solution_raw) - 1
                if 0 <= idx < len(choices):
                    solution = choices[idx]
                else:
                    solution = "정답 없음"
            else:
                solution = re.sub(r"^\d\.\s*", "", solution_raw)
        else:
            solution = solution_raw

        # 유형
        qtype_map = {
            "객관식": "객관식",
            "단답형": "단답형",
            "서술형": "단답형",
            "참/거짓": "OX",
        }
        qtype = qtype_map.get(qtype_raw, "기타")

        quiz_data = {
            "quiz_body": body,
            "solution": solution,
            "type": qtype
        }

        if choices:
            quiz_data["choices"] = choices

        quizzes.append(quiz_data)

    return quizzes