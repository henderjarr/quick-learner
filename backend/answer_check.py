# backend/answer_check.py
# Plain-code helpers for comparing answers (no AI involved).
# Used by main.py (grading) and ai_service.py (checking the AI's exercises).
import re


def normalize_answer(text: str) -> str:
    """Lowercase, trim, and drop surrounding punctuation so 'Perro.' matches 'perro'."""
    return text.strip().strip(".,!?¡¿;:\"'").strip().lower()


def remove_brackets(text):
    """Removes anything in brackets, like (dog)."""
    return re.sub(r"\([^)]*\)", "", text)


def contains_whole_word(sentence, word):
    """True if word appears on its own in sentence, ignoring capitals."""
    return (
        re.search(rf"(?<!\w){re.escape(word)}(?!\w)", sentence, re.IGNORECASE)
        is not None
    )
