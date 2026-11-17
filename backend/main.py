# backend/main.py
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import (
    VocabularyItemOut,
    AnswerSubmit,
    AnswerResult,
    ExerciseOut,
    FlashcardReviewResult,
    FlashcardReviewSubmit,
    ProgressOut,
    GroupOut,
)
import data_manager
import ai_service
from answer_check import normalize_answer

app = FastAPI()

PILE_SIZE = 10  # flashcards in a pile; topped up with new words when short

# Cors middleware, to allow cross platform communication
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
)

# Dependency: gives each request its own DB session, closes it afterward


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/vocabulary/{domain_id}", response_model=List[VocabularyItemOut])
def read_vocabulary(domain_id: int, db: Session = Depends(get_db)):
    items = data_manager.get_vocabulary_by_domain(db, domain_id)
    if not items:
        raise HTTPException(
            status_code=404, detail="No vocabulary found for this domain"
        )
    return items


# add to main.py


@app.post("/exercises/generate", response_model=ExerciseOut)
def generate_exercise(
    user_id: int,
    domain_id: int,
    # ids of words skipped this visit: ?exclude=12&exclude=40
    exclude: Annotated[List[int], Query()] = [],
    db: Session = Depends(get_db),
):
    domain = data_manager.get_domain_by_id(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    due_items = data_manager.get_due_vocabulary_items_for_user(
        db, user_id, exclude_ids=exclude
    )

    if not due_items:
        raise HTTPException(status_code=404, detail="Do some flashcards first")

    # a saved sentence for the target word that isn't solved yet? reuse it, no AI call
    saved = data_manager.find_open_exercise(db, user_id, domain_id, due_items[0].id)
    if saved:
        return saved

    try:
        exercise_data = ai_service.generate_exercise_from_words(
            domain_name=domain.name,
            system_prompt=domain.system_prompt,
            vocabulary_items=due_items,
        )
    except Exception as e:  # OpenAI down, or the AI kept breaking the rules
        print(f"AI generation failed: {e}")
        raise HTTPException(
            status_code=502, detail="AI could not generate an exercise, try again"
        )

    new_exercise = data_manager.create_exercise(
        db,
        domain_id=domain_id,
        type=exercise_data["type"],
        prompt=exercise_data["prompt"],
        correct_answer=exercise_data["correct_answer"],
        # the target word (the answer); SRS updates this word on submit
        vocabulary_item_id=due_items[0].id,
        generated_by_ai=True,
    )

    return new_exercise


@app.post("/exercises/{exercise_id}/submit", response_model=AnswerResult)
def submit_answer(
    exercise_id: int, submission: AnswerSubmit, db: Session = Depends(get_db)
):
    exercise = data_manager.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    domain = data_manager.get_domain_by_id(db, exercise.domain_id)

    # 1. Check the answer: plain code decides (fast, free, can't be wrong)
    is_correct = normalize_answer(submission.user_answer) == normalize_answer(
        exercise.correct_answer
    )

    # 2. Ask the AI to explain the result
    try:
        ai_feedback = ai_service.evaluate_answer(
            system_prompt=domain.system_prompt,
            exercise_prompt=exercise.prompt,
            correct_answer=exercise.correct_answer,
            user_answer=submission.user_answer,
            is_correct=is_correct,
        )
    except Exception as e:  # OpenAI down, bad JSON, etc.
        print(f"AI evaluation failed: {e}")
        # the answer is already graded, so carry on without feedback
        ai_feedback = None

    # 3. Save the attempt
    attempt = data_manager.create_attempt(
        db,
        user_id=submission.user_id,
        exercise_id=exercise.id,
        user_answer=submission.user_answer,
        is_correct=is_correct,
        ai_feedback=ai_feedback,
    )

    # 4. Update spaced repetition for the word this exercise is linked to
    next_review_at = None
    if exercise.vocabulary_item_id is not None:
        card = data_manager.get_or_create_srs_card(
            db, submission.user_id, exercise.vocabulary_item_id
        )
        card = data_manager.update_srs_card(db, card, is_correct)
        next_review_at = card.due_at

    return AnswerResult(
        attempt_id=attempt.id,
        is_correct=is_correct,
        correct_answer=exercise.correct_answer,
        ai_feedback=ai_feedback,
        next_review_at=next_review_at,
    )


@app.get("/flashcards/due", response_model=List[VocabularyItemOut])
def get_due_flashcards(
    user_id: int,
    domain_id: int,
    known: bool = False,
    topic: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if known:
        # reviewing known words: just return them (an empty list is fine)
        return data_manager.get_flashcards(
            db, user_id, domain_id, known=True, topic=topic
        )

    cards = data_manager.get_flashcards(db, user_id, domain_id, topic=topic)
    if len(cards) < PILE_SIZE:
        # top the pile up to PILE_SIZE with new words from the same topic,
        # so leftovers from an earlier session don't leave a tiny pile
        data_manager.introduce_new_words(
            db, user_id, domain_id, limit=PILE_SIZE - len(cards), topic=topic
        )
        cards = data_manager.get_flashcards(db, user_id, domain_id, topic=topic)
    return cards


# POST, not GET: this creates new SrsCard rows
@app.post("/flashcards/deal", response_model=List[VocabularyItemOut])
def deal_more_flashcards(
    user_id: int,
    domain_id: int,
    topic: Optional[str] = None,
    count: int = 10,
    db: Session = Depends(get_db),
):
    # start `count` new words (from the topic, if given) and return them.
    # An empty list means no new words are left (not an error).
    return data_manager.introduce_new_words(
        db, user_id, domain_id, limit=count, topic=topic
    )


@app.post(
    "/flashcards/{vocabulary_item_id}/review", response_model=FlashcardReviewResult
)
def review_flashcard(
    vocabulary_item_id: int,
    review: FlashcardReviewSubmit,
    db: Session = Depends(get_db),
):
    card = data_manager.get_or_create_srs_card(db, review.user_id, vocabulary_item_id)
    card = data_manager.review_flashcard(db, card, review.knew_it)
    return FlashcardReviewResult(
        vocabulary_item_id=vocabulary_item_id, stage=card.stage
    )


@app.get("/progress", response_model=ProgressOut)
def get_progress(user_id: int, domain_id: int, db: Session = Depends(get_db)):
    return data_manager.get_progress(db, user_id, domain_id)


@app.get("/groups", response_model=List[GroupOut])
def get_groups(domain_id: int, db: Session = Depends(get_db)):
    return data_manager.get_groups(db, domain_id)


# every word in one group, for practice mode (doesn't touch the schedule)
@app.get("/groups/{group_id}/words", response_model=List[VocabularyItemOut])
def get_group_words(group_id: int, db: Session = Depends(get_db)):
    return data_manager.get_group_words(db, group_id)
