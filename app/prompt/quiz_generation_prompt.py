from langchain.prompts import PromptTemplate
from app.core.memory import QuizMemory

quiz_prompt_template = PromptTemplate(
    input_variables=["context", "history_block", "audio_guide", "question"],
    template="""
다음은 강의 자료{audio_guide} 참고하여 만든 콘텐츠입니다.

{history_block}

다음 조건에 맞는 새로운 퀴즈를 생성해 주세요:

- 객관식 2문제 (보기 4개, 정답 포함)
- 단답형 주관식 1문제 (정답 포함)
- 참/거짓 문제 1문제 (정답 포함)
- 모든 문항은 반드시 한국어로 작성해 주세요.
※ 마크다운 문법을 사용하지 마세요. 모든 항목은 순수 텍스트로 작성해주세요.

🔹 단답형 문제 작성 시 주의사항:
- 정답이 여러 표현으로 존재하는 경우(예: 배깅, bagging)는 모두 포함하여 `,`로 구분된 하나의 줄로 작성해 주세요.
- 단, 여러 개를 작성하시오와 같은 복수입력형 문제가 되지 않도록 해 주세요.
  (예: “모두 작성하시오”, “다 고르시오”, “두 가지는 무엇인가요” 등은 절대 사용하지 마세요.)
- 문제 문장에도 반드시 "한 가지는 무엇인가요?", "무엇인가요?" 등 단일 정답을 유도하는 표현만 사용해 주세요.
- “두 가지”, “세 가지”, “모두”, “각각”, “~와 ~” 등의 표현은 문제 문장에 절대 포함되지 않도록 해 주세요.
- 예시 정답: 배깅, bagging

문장 스타일 지침:
- 객관식/주관식 문항은 “~을 고르세요”, “~은 무엇인가요?” 형태의 존댓말로 작성
- 참/거짓 문항은 “~이다”, “~하지 않는다” 형태의 평서문으로 작성
표기 규칙(아주 중요):
- LaTeX/TeX/수식 표기(예: $, \\(...\\), \\[...\\], \\alpha, \\beta, ^, _, {{ }}, \\\\)를 절대 사용하지 마세요.
- 그리스 문자는 한글/영문 이름으로 풀어서 쓰세요. 예: 알파(alpha), 베타(beta), 세타(theta)
- 특수문자 대신 순수 한글/영문만 사용하세요.

출력 형식 지침 (꼭 지켜주세요):
[문항 유형: 객관식]
문제: 바나나가 과일이 맞는 이유를 고르세요.
보기:
1. 보기내용1
2. 보기내용2
3. 보기내용3
4. 보기내용4
정답: 1. 보기내용1

[문항 유형: 단답형]
문제: 바나나는 무슨 색인가요?
정답: 노란색

[문항 유형: 참/거짓]
문제: 바나나는 영어로 banana이다.
정답: O 또는 X

📘 참조 문맥(강의자료/음성 추출):
{context}

<생성 요청>
{question}
"""
)

def make_quiz_prompt(memory: QuizMemory, audio_present: bool) -> PromptTemplate:
    history_block = ""
    if memory.get_all():
        history_block = (
            "※ 이전에 생성된 퀴즈는 다음과 같습니다. 동일하거나 유사한 문제는 절대 중복해서 생성하지 마세요.\n\n"
            "이전 퀴즈:\n" + "\n\n---\n\n".join(memory.get_all())
        )
    audio_guide = "와 일부 강의 음성 텍스트를" if audio_present else "를"
    return quiz_prompt_template.partial(
        history_block=history_block,
        audio_guide=audio_guide,
    )