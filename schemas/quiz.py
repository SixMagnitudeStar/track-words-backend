from pydantic import BaseModel
from typing import List

class QuizQuestion(BaseModel):
    """
    Represents a single quiz question.
    """
    id: int
    word: str
    options: List[str]
    correct_answer: str

    class Config:
        orm_mode = True

class QuizResponse(BaseModel):
    """
    Represents the full quiz response, which is a list of questions.
    """
    questions: List[QuizQuestion]
