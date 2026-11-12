# backend/data_manager.py
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from models import (
    Domain,
    VocabularyItem,
    GrammarRule,
    Exercise,
    UserExerciseAttempt,
    SrsCard,
    User,
    FlashcardReview,
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
    return (
        db.query(VocabularyItem)
        .filter(
            and_(
                VocabularyItem.domain_id == domain_id,
                VocabularyItem.cefr_level == cefr_level,
            )
        )
        .all()
    )


def get_vocabulary_item_by_id(db: Session, item_id: int):
    """Fetch a vocabulary item by its ID."""
    return db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()


def create_vocabulary_item(
    db: Session,
    domain_id: int,
    term: str,
    definition: str,
    example_sentence: str = None,
    cefr_level: str = None,
):
    item = VocabularyItem(
        domain_id=domain_id,
        term=term,
        definition=definition,
        example_sentence=example_sentence,
        cefr_level=cefr_level,
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_due_vocabulary_items_for_user(
    db: Session, user_id: int, stage: str = "exercise", limit: int = 3
):
    due_cards = get_due_cards_for_user(db, user_id, stage)
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


def create_grammar_rule(
    db: Session, domain_id: int, title: str, explanation: str, cefr_level: str = None
):
    rule = GrammarRule(
        domain_id=domain_id, title=title, explanation=explanation, cefr_level=cefr_level
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# ---------- Exercise ----------


def create_exercise(
    db: Session,
    domain_id: int,
    type: str,
    prompt: str,
    correct_answer: str,
    vocabulary_item_id: int = None,
    grammar_rule_id: int = None,
    generated_by_ai: bool = True,
):
    exercise = Exercise(
        domain_id=domain_id,
        type=type,
        vocabulary_item_id=vocabulary_item_id,
        grammar_rule_id=grammar_rule_id,
        prompt=prompt,
        correct_answer=correct_answer,
        generated_by_ai=generated_by_ai,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def get_exercise_by_id(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


# ---------- UserExerciseAttempt ----------


def create_attempt(
    db: Session,
    user_id: int,
    exercise_id: int,
    user_answer: str,
    is_correct: bool,
    ai_feedback: str = None,
):
    attempt = UserExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=is_correct,
        ai_feedback=ai_feedback,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempts_by_user(db: Session, user_id: int):
    return (
        db.query(UserExerciseAttempt)
        .filter(UserExerciseAttempt.user_id == user_id)
        .all()
    )


# ---------- SrsCard ----------


def get_due_cards_for_user(db: Session, user_id: int, stage: str):
    now = datetime.now(timezone.utc)
    return (
        db.query(SrsCard)
        .filter(
            and_(
                SrsCard.user_id == user_id,
                SrsCard.stage == stage,
                SrsCard.due_at <= now,
            )
        )
        .order_by(SrsCard.due_at)
        .all()
    )  # most overdue first


def get_flashcards(
    db: Session,
    user_id: int,
    domain_id: int,
    known: bool = False,
    topic: str = None,
    limit: int = 10,
):
    """
    Words for the flashcard screen.
    known=False: flashcard-stage words that are due, most overdue first, up to `limit`.
    known=True: every word already moved to practice, shuffled, due or not.
    """
    # start from the words, and attach each word's SRS card for this user
    query = (
        db.query(VocabularyItem)
        .join(SrsCard, SrsCard.vocabulary_item_id == VocabularyItem.id)
        .filter(SrsCard.user_id == user_id, VocabularyItem.domain_id == domain_id)
    )

    if topic:
        query = query.filter(VocabularyItem.topic == topic)

    if known:
        return query.filter(SrsCard.stage == "exercise").order_by(func.random()).all()

    now = datetime.now(timezone.utc)
    return (
        query.filter(SrsCard.stage == "flashcard", SrsCard.due_at <= now)
        .order_by(SrsCard.due_at)
        .limit(limit)
        .all()
    )


def get_or_create_srs_card(db: Session, user_id: int, vocabulary_item_id: int):
    card = (
        db.query(SrsCard)
        .filter(
            and_(
                SrsCard.user_id == user_id,
                SrsCard.vocabulary_item_id == vocabulary_item_id,
            )
        )
        .first()
    )

    if card is None:
        card = SrsCard(user_id=user_id, vocabulary_item_id=vocabulary_item_id)
        db.add(card)
        db.commit()
        db.refresh(card)

    return card


def review_flashcard(db: Session, card: SrsCard, knew_it: bool):
    """Saves one flashcard answer. "Got it" moves the word on to the exercise stage."""
    db.add(
        FlashcardReview(
            user_id=card.user_id,
            vocabulary_item_id=card.vocabulary_item_id,
            knew_it=knew_it,
        )
    )

    if knew_it:
        card.stage = "exercise"
    else:
        # "Still learning": the word belongs in the flashcard pile
        # (this is what moves a known word back when you've forgotten it)
        card.stage = "flashcard"
    # due now, in whichever pile it is in
    card.due_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(card)
    return card


def introduce_new_words(
    db: Session, user_id: int, domain_id: int, limit: int = 5, topic: str = None
):
    """
    Starts the user on the next words they haven't seen yet, by creating SRS cards (due now).
    Order: lowest CEFR level first, then teach_order tier, then random within a tier
    so topics get mixed instead of drilled one at a time.
    """
    # ids of words this user already has a card for
    started_ids = select(SrsCard.vocabulary_item_id).where(SrsCard.user_id == user_id)
    query = db.query(VocabularyItem).filter(
        and_(
            VocabularyItem.domain_id == domain_id,
            VocabularyItem.id.not_in(started_ids),
        )
    )
    if topic:
        query = query.filter(VocabularyItem.topic == topic)

    new_items = (
        query.order_by(
            VocabularyItem.cefr_level, VocabularyItem.teach_order, func.random()
        )
        .limit(limit)
        .all()
    )

    for item in new_items:
        db.add(SrsCard(user_id=user_id, vocabulary_item_id=item.id))
    db.commit()

    return new_items


def update_srs_card(db: Session, card: SrsCard, is_correct: bool):
    if is_correct:
        card.repetitions += 1
        card.interval_days = int(card.interval_days * card.ease_factor)
        card.ease_factor = min(card.ease_factor + 0.1, 3.0)
    else:
        card.repetitions = 0
        card.interval_days = 1
        card.ease_factor = max(card.ease_factor - 0.2, 1.3)

    card.due_at = datetime.now(timezone.utc) + timedelta(days=card.interval_days)

    db.commit()
    db.refresh(card)
    return card


def get_progress(db: Session, user_id: int, domain_id: int):
    """Counts for the Home screen."""
    return {
        # reuse the existing function, then count the list
        "flashcards_due": len(get_due_cards_for_user(db, user_id, "flashcard")),
        "exercises_due": len(get_due_cards_for_user(db, user_id, "exercise")),
        # every word that has reached the exercise stage, due or not
        "words_in_practice": db.query(SrsCard)
        .filter(and_(SrsCard.user_id == user_id, SrsCard.stage == "exercise"))
        .count(),
        "total_words": db.query(VocabularyItem)
        .filter(VocabularyItem.domain_id == domain_id)
        .count(),
    }


def get_topics(db: Session, user_id: int, domain_id: int):
    """Every topic in a domain with its word counts, for the Home screen."""
    # one row per word: its topic, and its card's stage (None if not started yet)
    rows = (
        db.query(VocabularyItem.topic, SrsCard.stage)
        .outerjoin(
            SrsCard,
            and_(
                SrsCard.vocabulary_item_id == VocabularyItem.id,
                SrsCard.user_id == user_id,
            ),
        )
        .filter(
            VocabularyItem.domain_id == domain_id,
            VocabularyItem.topic.isnot(None),
        )
        .all()
    )

    topics = {}
    for topic, stage in rows:
        if topic not in topics:
            topics[topic] = {
                "topic": topic,
                "total_words": 0,
                "learning": 0,
                "known": 0,
            }
        topics[topic]["total_words"] += 1
        if stage == "flashcard":
            topics[topic]["learning"] += 1
        elif stage == "exercise":
            topics[topic]["known"] += 1

    return sorted(topics.values(), key=lambda t: t["topic"])


# ---------- User ----------


def get_or_create_default_user(db: Session):
    user = db.query(User).first()

    if user is None:
        user = User(display_name="Learner")
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
