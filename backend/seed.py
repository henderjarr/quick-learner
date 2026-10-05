from database import SessionLocal
from models import Domain, VocabularyItem

db = SessionLocal()

spanish = Domain(name="Spanish", domain_type="language",
                 system_prompt="You are a patient Spanish tutor.")
db.add(spanish)
db.commit()
db.refresh(spanish)

words = [
    VocabularyItem(domain_id=spanish.id, term="perro",
                   definition="dog", cefr_level="A1"),
    VocabularyItem(domain_id=spanish.id, term="gato",
                   definition="cat", cefr_level="A1"),
    VocabularyItem(domain_id=spanish.id, term="hablar",
                   definition="to speak", cefr_level="A1"),
]
db.add_all(words)
db.commit()

db.close()
print("Seed data added.")
