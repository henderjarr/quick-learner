import { useState } from "react";
import type { Direction, Flashcard } from "../types";

type FlashcardViewProps = {
  card: Flashcard;
  direction: Direction;
  onAnswer: (knewIt: boolean) => void;
};

// the database stores "m" / "f" / "n"; the card writes it out
const genderNames: Record<string, string> = {
  m: "masculine",
  f: "feminine",
  n: "neuter",
};

function FlashcardView({ card, direction, onAnswer }: FlashcardViewProps) {
  const [flipped, setFlipped] = useState(false);

  const termFirst = direction === "term";
  // nouns are learned with their article: "la manzana"
  const fullTerm = card.article ? `${card.article} ${card.term}` : card.term;
  const genderName = card.gender ? genderNames[card.gender] : null;

  return (
    <div className="card flashcard">
      {card.part_of_speech && (
        <span className="type-label">{card.part_of_speech}</span>
      )}

      {/* front: the bare word, or its meaning, depending on the direction */}
      <h2 className="flashcard-term">
        {termFirst ? card.term : card.definition}
      </h2>

      {!flipped ? (
        <button onClick={() => setFlipped(true)}>Show answer</button>
      ) : (
        <>
          <p className="flashcard-meaning">
            {termFirst ? card.definition : fullTerm}
          </p>

          {genderName && (
            <p className="muted small">
              {termFirst ? `${fullTerm} · ${genderName}` : genderName}
            </p>
          )}

          {card.example_sentence && (
            <p className="flashcard-example">{card.example_sentence}</p>
          )}

          {card.usage_note && (
            <p className="muted small">Tip: {card.usage_note}</p>
          )}

          <div className="button-row">
            <button className="btn-learning" onClick={() => onAnswer(false)}>
              Still learning
            </button>
            <button className="btn-primary" onClick={() => onAnswer(true)}>
              Got it
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default FlashcardView;
