# backend/check_vocab.py
# Checks every vocabulary file in data/spanish/ for mistakes BEFORE seeding.
# Run from backend/:  python check_vocab.py
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "spanish"
REQUIRED_FIELDS = ["term", "definition", "example_sentence", "teach_order"]
# allowed values, so a typo like "vrb" gets caught
PARTS_OF_SPEECH = ["noun", "verb", "adjective", "adverb", "pronoun", "article", "preposition",
                   "conjunction", "question_word", "interjection", "possessive",
                   "demonstrative", "contraction", "quantifier", "number"]
CONJUGATION_TYPES = ["regular", "stem_change_e_ie", "stem_change_o_ue", "stem_change_e_i",
                     "stem_change_u_ue", "irregular_yo", "irregular"]

problems = []
warnings = []        # worth a look, but not always wrong
seen_terms = {}      # (term, part_of_speech) -> file it first appeared in
seen_sentences = {}  # example sentence -> term that used it first
total = 0

for path in sorted(DATA_DIR.glob("*.json")):
    if path.name == "domain.json":
        continue  # domain info, not a word list

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"{path.name}: not valid JSON ({e})")
        continue

    if not data.get("cefr_level"):
        problems.append(f"{path.name}: missing cefr_level at the top of the file")

    for item in data["items"]:
        total += 1
        term = item.get("term", "?")
        where = f"{path.name}: '{term}'"
        item_type = item.get("item_type", "word")
        pos = item.get("part_of_speech")

        # every item needs the basics
        for field in REQUIRED_FIELDS:
            if not item.get(field):
                problems.append(f"{where} is missing {field}")

        if item_type not in ("word", "phrase"):
            problems.append(f"{where} has item_type '{item_type}' (use word or phrase)")
        if item_type == "word" and not pos:
            problems.append(f"{where} is a word but has no part_of_speech")
        if pos and pos not in PARTS_OF_SPEECH:
            problems.append(f"{where} has unknown part_of_speech '{pos}'")
        if pos == "verb" and item.get("conjugation_type") not in CONJUGATION_TYPES:
            problems.append(f"{where} is a verb with a missing or unknown conjugation_type")
        if item.get("teach_order") not in (1, 2, 3):
            problems.append(f"{where} teach_order must be 1, 2 or 3")

        # nouns need an article AND a gender (they can differ, e.g. el agua is feminine)
        if pos == "noun":
            if not item.get("article"):
                problems.append(f"{where} is a noun with no article")
            if item.get("gender") not in ("m", "f"):
                problems.append(f"{where} is a noun with no gender (m or f)")

        # the definition is shown as the exercise hint, so it shouldn't contain the answer
        definition = item.get("definition", "")
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", definition, re.IGNORECASE):
            warnings.append(f"{where} appears in its own definition "
                            "(fine for cognates like 'hotel'; otherwise move the Spanish to usage_note)")

        # the same term can appear twice only as different parts of speech (mañana adverb / noun)
        key = (term.lower(), pos)
        if key in seen_terms:
            problems.append(f"{where} is a duplicate (also in {seen_terms[key]})")
        else:
            seen_terms[key] = path.name

        # varied example sentences help memory
        sentence = item.get("example_sentence")
        if sentence in seen_sentences:
            problems.append(
                f"{where} reuses the example sentence of '{seen_sentences[sentence]}'")
        else:
            seen_sentences[sentence] = term

print(f"Checked {total} items.")
if problems:
    print(f"{len(problems)} problem(s):")
    for problem in problems:
        print(" -", problem)
else:
    print("No problems found.")
if warnings:
    print(f"{len(warnings)} warning(s):")
    for warning in warnings:
        print(" -", warning)
