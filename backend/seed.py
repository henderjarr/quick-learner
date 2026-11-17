# backend/seed.py
# Sets up the database: tables, the Spanish domain, every word file in data/spanish/,
# the default learner and their first SRS cards.
# Safe to run again: existing words are updated in place (keeping their SRS progress),
# new words are added. Run from backend/:  python seed.py
import json
from pathlib import Path

from database import SessionLocal, engine, Base
from models import Domain, VocabularyItem, SrsCard, Group, WordGroup
import data_manager

DATA_DIR = Path(__file__).parent / "data" / "spanish"
STARTER_WORDS = 10  # how many SRS cards a brand-new learner starts with

# readable names for the topic keys in the word files ("food_drink" -> "Food and drink")
TOPIC_NAMES = {
    "core": "Core basics",
    "everyday": "Everyday",
    "introductions": "Introductions",
    "people_family": "People and family",
    "food_drink": "Food and drink",
    "home": "Home",
    "daily_routine": "Daily routine",
    "body_health": "Body and health",
    "city_transport": "City and transport",
    "shopping_clothes": "Shopping and clothes",
    "free_time_weather": "Free time and weather",
    "numbers_time": "Numbers and time",
    "work_study": "Work and study",
}

# grammar groups that come straight from part_of_speech
POS_GROUPS = {
    "conjunction": "Conjunctions",
    "pronoun": "Pronouns",
    "preposition": "Prepositions",
    "question_word": "Question words",
    "article": "Articles",
    "possessive": "Possessives",
    "demonstrative": "Demonstratives",
}


def topic_name(topic: str) -> str:
    """A readable name for a topic key; unknown keys get "Some topic" style."""
    if topic in TOPIC_NAMES:
        return TOPIC_NAMES[topic]
    words = topic.replace("_", " ")
    return words[0].upper() + words[1:]


def grammar_groups_for(item: VocabularyItem, extra_groups: list) -> list:
    """Every grammar group a word belongs to: from its data, plus any "groups" key in the JSON."""
    names = list(extra_groups)  # e.g. ["Modal verbs"]
    if item.part_of_speech in POS_GROUPS:
        names.append(POS_GROUPS[item.part_of_speech])

    kind = item.conjugation_type or ""
    if kind == "regular":
        names.append("Regular verbs")
    elif kind.startswith("stem_change"):
        names.append("Stem-changing verbs")
    elif kind in ("irregular", "irregular_yo"):
        names.append("Irregular verbs")

    if item.part_of_speech == "verb" and item.term.endswith("se"):
        names.append("Reflexive verbs")  # lavarse, llamarse...

    # dict.fromkeys removes duplicates but keeps the order
    return list(dict.fromkeys(names))

# every column a word file can set (anything else in the JSON is ignored)
ITEM_FIELDS = ["term", "definition", "usage_note", "example_sentence", "cefr_level",
               "part_of_speech", "article", "gender", "feminine_form",
               "conjugation_type", "topic", "teach_order", "item_type"]

# 1. Create any missing tables (this never changes tables that already exist)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# 2. Domain: create it, or update it if domain.json changed (prompts are data)
domain_info = json.loads((DATA_DIR / "domain.json").read_text(encoding="utf-8"))
domain = db.query(Domain).filter(Domain.name == domain_info["name"]).first()
if domain is None:
    domain = Domain(name=domain_info["name"])
    db.add(domain)
domain.domain_type = domain_info["domain_type"]
domain.system_prompt = domain_info["system_prompt"]
db.commit()
db.refresh(domain)

# 3. Words: find what's already in the db, keyed by (term, part_of_speech)
#    so mañana (adverb) and mañana (noun) stay separate
existing = {
    (item.term, item.part_of_speech): item
    for item in data_manager.get_vocabulary_by_domain(db, domain.id)
}
added = 0
updated = 0
extra_groups = {}  # (term, part_of_speech) -> the word's "groups" list from the JSON

for path in sorted(DATA_DIR.glob("*.json")):
    if path.name in ("domain.json", "irregular_verbs.json"):
        continue  # domain info and verb tables, not word lists
    data = json.loads(path.read_text(encoding="utf-8"))

    for raw_item in data["items"]:
        # start from the file's defaults, then let the item override them
        values = {"cefr_level": data["cefr_level"],
                  "topic": data.get("topic"), "item_type": "word"}
        values.update(raw_item)

        key = (values["term"], values.get("part_of_speech"))
        item = existing.get(key)
        if item is None:
            item = VocabularyItem(domain_id=domain.id)
            db.add(item)
            existing[key] = item
            added += 1
        else:
            updated += 1

        # copy every field; a field missing from the JSON becomes None (so deleting it clears it)
        for field in ITEM_FIELDS:
            setattr(item, field, values.get(field))
        extra_groups[key] = values.get("groups", [])

db.commit()
print(f"Domain '{domain.name}' (id {domain.id}): {added} words added, {updated} updated.")

# 4. Groups: work out every (kind, group name, word), then rebuild the links from scratch
memberships = []
for key, item in existing.items():
    if item.topic:
        memberships.append(("topic", topic_name(item.topic), item))
    for name in grammar_groups_for(item, extra_groups.get(key, [])):
        memberships.append(("grammar", name, item))

groups = {g.name: g for g in db.query(Group).filter(Group.domain_id == domain.id)}
for kind, name, _ in memberships:
    if name not in groups:
        groups[name] = Group(domain_id=domain.id, name=name, kind=kind)
        db.add(groups[name])
db.flush()  # sends the new groups to the db so they get their ids

# old links out, fresh links in (so a word removed from a group really leaves it)
group_ids = [g.id for g in groups.values()]
db.query(WordGroup).filter(WordGroup.group_id.in_(group_ids)).delete(
    synchronize_session=False
)
for _, name, item in memberships:
    db.add(WordGroup(group_id=groups[name].id, vocabulary_item_id=item.id))
db.commit()
print(f"Groups: {len(groups)} groups, {len(memberships)} word links.")

# 5. Default learner, plus starter cards if they don't have any yet
user = data_manager.get_or_create_default_user(db)
card_count = db.query(SrsCard).filter(SrsCard.user_id == user.id).count()
if card_count == 0:
    new_words = data_manager.introduce_new_words(db, user.id, domain.id, limit=STARTER_WORDS)
    print(f"Created {len(new_words)} starter cards for user {user.id}: "
          + ", ".join(word.term for word in new_words))
else:
    print(f"User {user.id} already has {card_count} cards, none added.")

db.close()
