# backend/seed.py
# Sets up the database: tables, the Spanish domain, every word file in data/spanish/,
# the default learner and their first SRS cards.
# Safe to run again: existing words are updated in place (keeping their SRS progress),
# new words are added. Run from backend/:  python seed.py
import json
from pathlib import Path

from database import SessionLocal, engine, Base
from models import Domain, VocabularyItem, SrsCard
import data_manager

DATA_DIR = Path(__file__).parent / "data" / "spanish"
STARTER_WORDS = 10  # how many SRS cards a brand-new learner starts with

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

for path in sorted(DATA_DIR.glob("*.json")):
    if path.name == "domain.json":
        continue  # domain info, not a word list
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

db.commit()
print(f"Domain '{domain.name}' (id {domain.id}): {added} words added, {updated} updated.")

# 4. Default learner, plus starter cards if they don't have any yet
user = data_manager.get_or_create_default_user(db)
card_count = db.query(SrsCard).filter(SrsCard.user_id == user.id).count()
if card_count == 0:
    new_words = data_manager.introduce_new_words(db, user.id, domain.id, limit=STARTER_WORDS)
    print(f"Created {len(new_words)} starter cards for user {user.id}: "
          + ", ".join(word.term for word in new_words))
else:
    print(f"User {user.id} already has {card_count} cards, none added.")

db.close()
