# backend/seed_srs.py
from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import SrsCard
import data_manager

db = SessionLocal()

user = data_manager.get_or_create_default_user(db)
spanish = data_manager.get_domain_by_id(db, 1)  # your Spanish domain
words = data_manager.get_vocabulary_by_domain(db, spanish.id)

# Create a due SrsCard for each seeded word, backdated so due_at is already in the past
for word in words:
    card = SrsCard(
        user_id=user.id,
        vocabulary_item_id=word.id,
        # due yesterday = due now
        due_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    db.add(card)

db.commit()
db.close()
print(f"Created {len(words)} due SRS cards for user {user.id}.")
