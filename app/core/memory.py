from typing import Dict, List

lecture_memories: Dict[str, "QuizMemory"] = {}


class QuizMemory:
    def __init__(self, max_items: int = 50):
        """
        max_items: 보관할 최대 퀴즈 개수 (초과 시 FIFO로 가장 오래된 항목 제거)
        """
        self._previous_quizzes: List[str] = []
        self._max_items = max_items

    def add(self, quiz_text: str) -> None:
        """새로 생성된 퀴즈 텍스트를 추가한다."""
        if not isinstance(quiz_text, str) or not quiz_text.strip():
            return
        self._previous_quizzes.append(quiz_text.strip())

        if len(self._previous_quizzes) > self._max_items:
            overflow = len(self._previous_quizzes) - self._max_items
            del self._previous_quizzes[:overflow]

    def get_all(self) -> List[str]:
        return list(self._previous_quizzes)

    def clear(self) -> None:
        self._previous_quizzes.clear()

    def __len__(self) -> int:
        return len(self._previous_quizzes)


def get_lecture_memory(lecture_id: str) -> QuizMemory:
    if lecture_id not in lecture_memories:
        lecture_memories[lecture_id] = QuizMemory()
    return lecture_memories[lecture_id]


def reset_lecture_memory(lecture_id: str) -> bool:
    return lecture_memories.pop(lecture_id, None) is not None


def clear_lecture_memory(lecture_id: str) -> bool:
    mem = lecture_memories.get(lecture_id)
    if not mem:
        return False
    mem.clear()
    return True