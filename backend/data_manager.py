# backend/data_manager.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta
from models import (
    Domain, VocabularyItem, GrammarRule, Exercise,
    UserExerciseAttempt, SrsCard, User
)

# ---------- Domain ----------


def get_all_domains(db: Session):
    """Fetch all domains from the database."""
    return db.query(Domain).all()


def get_domain_by_id(db: Session, domain_id: int):
    """Fetch a domain by its ID."""
    return db.query(Domain).filter(Domain.id == domain_id).first()


# ---------- VocabularyItem ----------

def get_vocabulary_by_domain(db: Session, domain_id: int):
    """Fetch all vocabulary items for a specific domain."""
    return db.query(VocabularyItem).filter(VocabularyItem.domain_id == domain_id).all()


def get_vocabulary_by_domain_and_level(db: Session, domain_id: int, cefr_level: str):
    """Fetch vocabulary items for a specific domain and CEFR level."""
    return db.query(VocabularyItem).filter(
        and_(
            VocabularyItem.domain_id == domain_id,
            VocabularyItem.cefr_level == cefr_level
        )
    ).all()


def get_vocabulary_item_by_id(db: Session, item_id: int):
    """Fetch a vocabulary item by its ID."""
    return db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()


def create_vocabulary_item(db: Session, domain_id: int, term: str, definition: str, example_sentence: str = None, cefr_level: str = None):
    item = VocabularyItem(
        domain_id=domain_id,
        term=term,
        definition=definition,
        example_sentence=example_sentence,
        cefr_level=cefr_level
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_due_vocabulary_items_for_user(db: Session, user_id: int, limit: int = 3):
    due_cards = get_due_cards_for_user(db, user_id)
    items = []
    for card in due_cards[:limit]:
        item = get_vocabulary_item_by_id(db, card.vocabulary_item_id)
        if item:
            items.append(item)
    return items

# ---------- GrammarRule ----------


def get_grammar_rules_by_domain(db: Session, domain_id: int):
    return db.query(GrammarRule).filter(GrammarRule.domain_id == domain_id).all()


def get_grammar_rule_by_id(db: Session, rule_id: int):
    return db.query(GrammarRule).filter(GrammarRule.id == rule_id).first()


def create_grammar_rule(db: Session, domain_id: int, title: str, explanation: str,
                        cefr_level: str = None):
    rule = GrammarRule(
        domain_id=domain_id,
        title=title,
        explanation=explanation,
        cefr_level=cefr_level
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# ---------- Exercise ----------

def create_exercise(db: Session, domain_id: int, type: str, prompt: str, correct_answer: str,
                    vocabulary_item_id: int = None, grammar_rule_id: int = None,
                    generated_by_ai: bool = True):
    exercise = Exercise(
        domain_id=domain_id,
        type=type,
        vocabulary_item_id=vocabulary_item_id,
        grammar_rule_id=grammar_rule_id,
        prompt=prompt,
        correct_answer=correct_answer,
        generated_by_ai=generated_by_ai
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def get_exercise_by_id(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


# ---------- UserExerciseAttempt ----------

def create_attempt(db: Session, user_id: int, exercise_id: int, user_answer: str,
                   is_correct: bool, ai_feedback: str = None):
    attempt = UserExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=is_correct,
        ai_feedback=ai_feedback
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempts_by_user(db: Session, user_id: int):
    return db.query(UserExerciseAttempt).filter(UserExerciseAttempt.user_id == user_id).all()


# ---------- SrsCard ----------

def get_due_cards_for_user(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    return db.query(SrsCard).filter(
        and_(
            SrsCard.user_id == user_id,
            SrsCard.due_at <= now
        )
    ).all()


def get_or_create_srs_card(db: Session, user_id: int, vocabulary_item_id: int):
    card = db.query(SrsCard).filter(
        and_(
            SrsCard.user_id == user_id,
            SrsCard.vocabulary_item_id == vocabulary_item_id
        )
    ).first()

    if card is None:
        card = SrsCard(user_id=user_id, vocabulary_item_id=vocabulary_item_id)
        db.add(card)
        db.commit()
        db.refresh(card)

    return card


def update_srs_card(db: Session, card: SrsCard, is_correct: bool):
    if is_correct:
        card.repetitions += 1
        card.interval_days = int(card.interval_days * card.ease_factor)
        card.ease_factor = min(card.ease_factor + 0.1, 3.0)
    else:
        card.repetitions = 0
        card.interval_days = 1
        card.ease_factor = max(card.ease_factor - 0.2, 1.3)

    card.due_at = datetime.now(timezone.utc) + \
        timedelta(days=card.interval_days)

    db.commit()
    db.refresh(card)
    return card


# ---------- User ----------

def get_or_create_default_user(db: Session):
    user = db.query(User).first()

    if user is None:
        user = User(display_name="Learner")
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
