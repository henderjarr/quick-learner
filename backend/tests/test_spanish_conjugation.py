"""Tests for the Spanish present-tense tables in conjugations/spanish.py (no AI involved)."""

from conjugations.spanish import present_tense


def forms_only(table):
    """Keeps just the verb forms from a list of (person, form) pairs."""
    return [form for person, form in table]


def test_present_tense_regular_ar_verb():
    """hablar is regular: the stem 'habl' plus the -ar endings."""
    assert forms_only(present_tense("hablar", "regular")) == [
        "hablo",
        "hablas",
        "habla",
        "hablamos",
        "habláis",
        "hablan",
    ]


def test_present_tense_stem_changing_e_to_ie():
    """pensar changes e -> ie, except for nosotros and vosotros (pensamos, pensáis)."""
    assert forms_only(present_tense("pensar", "stem_change_e_ie")) == [
        "pienso",
        "piensas",
        "piensa",
        "pensamos",
        "pensáis",
        "piensan",
    ]


def test_present_tense_returns_none_for_gustar():
    """gustar gets no table: you say 'me gusta', not 'yo gusto', so a yo/tú/él table would mislead."""
    assert present_tense("gustar", "regular") is None


def test_present_tense_phrase_conjugates_only_the_first_word():
    """In 'tener que' only 'tener' changes (irregular, from the JSON file); 'que' stays."""
    assert forms_only(present_tense("tener que", None))[0] == "tengo que"
