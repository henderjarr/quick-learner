"""Tests for my plain-code answer helpers in answer_check.py (no AI involved)."""

from answer_check import normalize_answer, find_missing_accents, contains_whole_word

# TIP: use a long test name that says what is being checked, name tells you what broke
# Rule of thumb: one test = one behaviour.


def test_normalize_answer_removes_spaces_punctuation_and_capitals():
    """Extra spaces, a full stop and a capital letter are all removed."""
    assert normalize_answer("  Perro. ") == "perro"


def test_normalize_answer_removes_spanish_question_marks():
    """The Spanish ¿ ? marks go, but the words and accents inside stay."""
    assert normalize_answer("¿Cuánto cuesta?") == "cuánto cuesta"


def test_normalize_answer_keeps_accents():
    """Accents are NOT removed, because accent mistakes are graded separately."""
    assert normalize_answer("Café") == "café"


def test_find_missing_accents_returns_none_when_answer_is_correct():
    """A correct answer has no accent mistake, so it returns None."""
    assert find_missing_accents("café", "café") is None


def test_find_missing_accents_returns_the_missing_letter():
    """'cafe' for 'café' is an accent-only mistake, so it returns the correct letter."""
    assert find_missing_accents("cafe", "café") == ["é"]


def test_find_missing_accents_returns_none_for_a_different_word():
    """'perro' for 'gato' is more than an accent mistake, so it returns None."""
    assert find_missing_accents("perro", "gato") is None


def test_contains_whole_word_finds_the_word_on_its_own():
    """'perro' is a separate word in the sentence, so it's found."""
    assert contains_whole_word("Tengo un perro.", "perro") is True


def test_contains_whole_word_ignores_the_word_inside_a_longer_word():
    """'de' is inside 'desayuno' but not a word on its own, so it's not found."""
    assert contains_whole_word("El desayuno es bueno", "de") is False


def test_contains_whole_word_ignores_capital_letters():
    """'Perro' with a capital still counts as the word 'perro'."""
    assert contains_whole_word("Perro grande", "perro") is True
