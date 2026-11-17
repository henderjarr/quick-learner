# pydantic schemas for the User and Question models

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# one row of a conjugation table: ("yo", "hablo")
class FormOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    form: str


class VocabularyItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    term: str
    definition: str
    example_sentence: Optional[str] = None
    cefr_level: Optional[str] = None
    usage_note: Optional[str] = None  # the tip on the card back
    part_of_speech: Optional[str] = None  # "noun", "verb"...
    article: Optional[str] = None  # nouns: "el", "la"
    gender: Optional[str] = None  # nouns: "m", "f"
    topic: Optional[str] = None
    forms: List[FormOut] = []  # verbs: the present-tense table (empty for other words)


# what the client gets when an exercise is handed out.
# correct_answer is NOT listed, so FastAPI leaves it out of the response.
class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    prompt: str
    vocabulary_item_id: Optional[int] = None  # the target word (needed for skipping)


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


# one entry in the list dropdown (a topic or a grammar group)
class GroupOut(BaseModel):
    id: int
    name: str
    kind: str  # "topic" or "grammar"
    word_count: int
