# backend/conjugations/spanish.py
# Spanish present-tense tables, worked out in plain code (no AI).
# Irregular verbs come from the checked file data/spanish/irregular_verbs.json;
# regular and stem-changing verbs are computed from their conjugation_type.
# One file per language in this folder (german.py later).
import json
from pathlib import Path

# .parent = conjugations/, .parent.parent = backend/ (where data/ lives)
_IRREGULAR_FILE = (
    Path(__file__).parent.parent / "data" / "spanish" / "irregular_verbs.json"
)
_irregular_data = json.loads(_IRREGULAR_FILE.read_text(encoding="utf-8"))

PERSONS = _irregular_data["persons"]  # ["yo", "tú", "él/ella/usted", ...]
IRREGULAR = _irregular_data["verbs"]  # {"ser": ["soy", "eres", ...], ...}

# regular endings, in the same order as PERSONS
ENDINGS = {
    "ar": ["o", "as", "a", "amos", "áis", "an"],
    "er": ["o", "es", "e", "emos", "éis", "en"],
    "ir": ["o", "es", "e", "imos", "ís", "en"],
}

# conjugation_type -> (vowel in the stem, what it becomes)
STEM_CHANGES = {
    "stem_change_e_ie": ("e", "ie"),  # pensar -> pienso
    "stem_change_o_ue": ("o", "ue"),  # volver -> vuelvo
    "stem_change_e_i": ("e", "i"),  # pedir -> pido
    "stem_change_u_ue": ("u", "ue"),  # jugar -> juego
}
NO_STEM_CHANGE = (3, 4)  # nosotros and vosotros keep the normal stem (pensamos)

REFLEXIVE_PRONOUNS = ["me", "te", "se", "nos", "os", "se"]

# no person-by-person table makes sense for these
NO_TABLE = {"hay", "gustar", "encantar", "doler"}
# weather verbs only have one form
ONLY_FORMS = {"llover": [("él/ella/usted", "llueve")]}


def change_last_vowel(stem: str, old: str, new: str) -> str:
    """Changes the LAST `old` vowel in the stem: "despert" -> "despiert"."""
    i = stem.rfind(old)
    if i == -1:
        return stem
    return stem[:i] + new + stem[i + 1:]


def present_tense(term: str, conjugation_type: str | None):
    """
    The present-tense table for a verb (or a phrase starting with an irregular verb),
    as a list of (person, form) pairs. Returns None when there is no table.
    """
    if term in NO_TABLE:
        return None
    if term in ONLY_FORMS:
        return ONLY_FORMS[term]

    # 1. checked data always wins (this also covers enviar's accents)
    if term in IRREGULAR:
        return list(zip(PERSONS, IRREGULAR[term]))

    # 2. a phrase like "tener que": conjugate the first word, keep the rest
    if " " in term:
        first, rest = term.split(" ", 1)
        if first in IRREGULAR:
            return [(p, f"{form} {rest}") for p, form in zip(PERSONS, IRREGULAR[first])]
        return None

    if not conjugation_type:
        return None

    # 3. reflexive: conjugate without "se", then put the pronoun in front (me lavo)
    if term.endswith("se"):
        base = present_tense(term[:-2], conjugation_type)
        if base is None:
            return None
        return [
            (person, f"{pronoun} {form}")
            for (person, form), pronoun in zip(base, REFLEXIVE_PRONOUNS)
        ]

    # 4. regular or stem-changing: stem + ending
    ending = term[-2:]  # "ar", "er" or "ir"
    if ending not in ENDINGS:
        return None
    stem = term[:-2]

    forms = []
    for i, end in enumerate(ENDINGS[ending]):
        this_stem = stem
        if conjugation_type in STEM_CHANGES and i not in NO_STEM_CHANGE:
            old, new = STEM_CHANGES[conjugation_type]
            this_stem = change_last_vowel(stem, old, new)
        forms.append(this_stem + end)
    return list(zip(PERSONS, forms))
