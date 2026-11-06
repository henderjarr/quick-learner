# backend/answer_check.py
# Plain-code helpers for comparing answers (no AI involved).
# Used by main.py (grading) and ai_service.py (checking the AI's exercises).
import re
import unicodedata


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


def remove_accents(text):
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def find_missing_accents(user_answer, correct_answer):
    user = unicodedata.normalize("NFC", user_answer.strip().lower())
    correct = unicodedata.normalize("NFC", correct_answer.strip().lower())
    if user == correct or remove_accents(user) != remove_accents(correct):
        return None
    return [c for u, c in zip(user, correct) if u != c]
