# pydantic schemas for the User and Question models

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class VocabularyItemOut(BaseModel):
    id: int
    term: str
    definition: str
    example_sentence: Optional[str] = None
    cefr_level: Optional[str] = None

    class Config:
        from_attributes = True


# what the client sends when answering an exercise
class AnswerSubmit(BaseModel):
    user_id: int
    user_answer: str


# what the client gets back after submitting an answer
class AnswerResult(BaseModel):
    attempt_id: int
    is_correct: bool
    correct_answer: str
    ai_feedback: Optional[str] = None
    # when the word comes up for review again (None if no word is linked)
    next_review_at: Optional[datetime] = None


# what the client sends when answering a flashcard
class FlashcardReviewSubmit(BaseModel):
    user_id: int
    knew_it: bool  # True = "Got it", False = "Still learning"


# what the client gets back: which pile the word is in now
class FlashcardReviewResult(BaseModel):
    vocabulary_item_id: int
    stage: str


# numbers for the Home screen
class ProgressOut(BaseModel):
    flashcards_due: int
    exercises_due: int
    words_in_practice: int
    total_words: int
