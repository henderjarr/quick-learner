# backend/main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import VocabularyItemOut, AnswerSubmit, AnswerResult
import data_manager
import ai_service


app = FastAPI()

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
            status_code=404, detail="No vocabulary found for this domain")
    return items

# add to main.py


@app.post("/exercises/generate")
def generate_exercise(user_id: int, domain_id: int, db: Session = Depends(get_db)):
    domain = data_manager.get_domain_by_id(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    due_items = data_manager.get_due_vocabulary_items_for_user(db, user_id)
    if not due_items:
        raise HTTPException(
            status_code=404, detail="No due vocabulary for this user")

    exercise_data = ai_service.generate_exercise_from_words(
        domain_name=domain.name,
        system_prompt=domain.system_prompt,
        vocabulary_items=due_items
    )

    new_exercise = data_manager.create_exercise(
        db,
        domain_id=domain_id,
        type=exercise_data["type"],
        prompt=exercise_data["prompt"],
        correct_answer=exercise_data["correct_answer"],
        # primary word this exercise is centered on
        vocabulary_item_id=due_items[0].id,
        generated_by_ai=True
    )

    return new_exercise


def normalize_answer(text: str) -> str:
    """Lowercase, trim, and drop surrounding punctuation so 'Perro.' matches 'perro'."""
    return text.strip().strip(".,!?¡¿;:\"'").strip().lower()


@app.post("/exercises/{exercise_id}/submit", response_model=AnswerResult)
def submit_answer(exercise_id: int, submission: AnswerSubmit, db: Session = Depends(get_db)):
    exercise = data_manager.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    domain = data_manager.get_domain_by_id(db, exercise.domain_id)

    # 1. Check the answer.
    # fill_blank has one right word, so plain code decides (fast, free, can't be wrong).
    # Open-ended types can be correct in many ways, so the AI decides.
    if exercise.type == "fill_blank":
        known_is_correct = normalize_answer(submission.user_answer) == \
            normalize_answer(exercise.correct_answer)
    else:
        known_is_correct = None

    # 2. Ask the AI for feedback (and a verdict, for open-ended types)
    try:
        evaluation = ai_service.evaluate_answer(
            system_prompt=domain.system_prompt,
            exercise_prompt=exercise.prompt,
            correct_answer=exercise.correct_answer,
            user_answer=submission.user_answer,
            known_is_correct=known_is_correct
        )
        ai_feedback = evaluation["feedback"]
        is_correct = known_is_correct if known_is_correct is not None \
            else evaluation["is_correct"]
    except Exception as e:  # OpenAI down, bad JSON, etc.
        print(f"AI evaluation failed: {e}")
        if known_is_correct is None:
            # open-ended answers can't be graded without the AI
            raise HTTPException(
                status_code=502, detail="AI evaluation failed, try again")
        # fill_blank is already graded, so carry on without feedback
        is_correct = known_is_correct
        ai_feedback = None

    # 3. Save the attempt
    attempt = data_manager.create_attempt(
        db,
        user_id=submission.user_id,
        exercise_id=exercise.id,
        user_answer=submission.user_answer,
        is_correct=is_correct,
        ai_feedback=ai_feedback
    )

    # 4. Update spaced repetition for the word this exercise is linked to
    next_review_at = None
    if exercise.vocabulary_item_id is not None:
        card = data_manager.get_or_create_srs_card(
            db, submission.user_id, exercise.vocabulary_item_id)
        card = data_manager.update_srs_card(db, card, is_correct)
        next_review_at = card.due_at

    return AnswerResult(
        attempt_id=attempt.id,
        is_correct=is_correct,
        correct_answer=exercise.correct_answer,
        ai_feedback=ai_feedback,
        next_review_at=next_review_at
    )
