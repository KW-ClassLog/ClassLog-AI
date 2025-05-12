import re

# response 구조 변환 함수
def parse_quiz_output(raw_text: str) -> list[dict]:
    quizzes = []
    blocks = re.split(r"\[문항 유형: (.*?)\]", raw_text.strip())

    for i in range(1, len(blocks), 2):
        qtype_raw = blocks[i].strip()
        content = blocks[i + 1].strip()

        body_match = re.search(r"문제:\s*(.+)", content)
        body = body_match.group(1).strip() if body_match else "질문 없음"

        sol_match = re.search(r"정답:\s*(.+)", content)
        solution_raw = sol_match.group(1).strip() if sol_match else "정답 없음"

        choices = []
        if "객관식" in qtype_raw:
            choices_block_match = re.search(r"보기:\s*(.*?)(?=정답:)", content, re.DOTALL)
            choices = []
            if choices_block_match:
                choices_block = choices_block_match.group(1).strip()
                choice_lines = re.findall(r"^\s*\d+\.\s+.+", choices_block, re.MULTILINE)
                choices = [re.sub(r"^\s*\d+\.\s*", "", line).strip() for line in choice_lines]

            if solution_raw.isdigit():
                idx = int(solution_raw) - 1
                if 0 <= idx < len(choices):
                    solution = choices[idx]
                else:
                    solution = "정답 없음"
            else:
                solution = re.sub(r"^\s*\d+\.\s*", "", solution_raw).strip()
                
        else:
            solution = solution_raw

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