# 퀴즈 생성을 위한 프롬프트 구성 + 이전 퀴즈 저장용 클래스
class QuizMemory:
    def __init__(self):
        self.previous_quizzes = []

    def add(self, quiz_text: str):
        self.previous_quizzes.append(quiz_text)

    def get_all(self):
        return self.previous_quizzes

    def get_prompt(self, document_text: str, audio_text: str):
        history = "\n\n---\n\n".join(self.previous_quizzes)

        if audio_text.strip():
            return f"""
다음은 강의 자료와 일부 강의 음성 텍스트를 참고하여 만든 콘텐츠입니다.  
음성 텍스트는 강의자료에서 누락된 보조 설명이므로, 퀴즈 생성 시 참고 정도로만 활용해 주세요.

※ 이전에 생성된 퀴즈는 다음과 같습니다. 동일하거나 유사한 문제는 절대 중복해서 생성하지 마세요.

이전 퀴즈:
{history}

다음 조건에 맞는 새로운 퀴즈를 생성해 주세요:

- 객관식 2문제 (보기 4개, 정답 포함)
- 단답형 주관식 1문제 (정답 포함)
- 참/거짓 문제 1문제 (정답 포함)
- 모든 문항은 반드시 한국어로 작성해 주세요.

문장 스타일 지침:
- 객관식/주관식 문항은 “~을 고르세요”, “~은 무엇인가요?” 형태의 존댓말로 작성
- 참/거짓 문항은 “~이다”, “~하지 않는다” 형태의 평서문으로 작성

📘 강의자료:
{document_text}

🎧 음성 텍스트 (보조 참고용):
{audio_text}
"""
        else:
            return f"""
다음은 강의 자료를 참고하여 만든 콘텐츠입니다.  
※ 이전에 생성된 퀴즈는 다음과 같습니다. 동일하거나 유사한 문제는 절대 중복해서 생성하지 마세요.

이전 퀴즈:
{history}

다음 조건에 맞는 새로운 퀴즈를 생성해 주세요:

- 객관식 2문제 (보기 4개, 정답 포함)
- 단답형 주관식 1문제 (정답 포함)
- 참/거짓 문제 1문제 (정답 포함)
- 모든 문항은 반드시 한국어로 작성해 주세요.

문장 스타일 지침:
- 객관식/주관식 문항은 “~을 고르세요”, “~은 무엇인가요?” 형태의 존댓말로 작성
- 참/거짓 문항은 “~이다”, “~하지 않는다” 형태의 평서문으로 작성

📘 강의자료:
{document_text}
"""
