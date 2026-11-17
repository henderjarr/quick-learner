import { useState } from "react";
import type { Direction, Flashcard } from "../types";

type FlashcardViewProps = {
  card: Flashcard;
  direction: Direction;
  // optional: without it (practice mode) the card has no Still learning / Got it
  onAnswer?: (knewIt: boolean) => void;
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
    <article className="card flashcard" aria-label="Flashcard">
      {/* front: the bare word, or its meaning, depending on the direction */}
      <div className="flashcard-front">
        {card.part_of_speech && (
          <span className="eyebrow">{card.part_of_speech}</span>
        )}
        <h2 className="flashcard-term">
          {termFirst ? card.term : card.definition}
        </h2>
      </div>

      {!flipped ? (
        <div className="flashcard-reveal">
          <button onClick={() => setFlipped(true)}>Show answer</button>
        </div>
      ) : (
        <>
          <div className="flashcard-back">
            <p className="flashcard-meaning">
              {termFirst ? card.definition : fullTerm}
            </p>

            {genderName && (
              <p className="muted">
                {termFirst ? `${fullTerm} · ${genderName}` : genderName}
              </p>
            )}

            {card.example_sentence && (
              <p className="flashcard-example">{card.example_sentence}</p>
            )}

            {card.forms.length > 0 && (
              <table className="conjugation">
                <caption className="eyebrow">Present tense</caption>
                <tbody>
                  {card.forms.map((row) => (
                    <tr key={row.label}>
                      <th scope="row">{row.label}</th>
                      <td>{row.form}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {card.usage_note && (
              <p className="tip">
                <strong>Tip:</strong> {card.usage_note}
              </p>
            )}
          </div>

          {onAnswer && (
            <div className="flashcard-actions">
              <button className="btn-learning" onClick={() => onAnswer(false)}>
                Still learning
              </button>
              <button className="btn-primary" onClick={() => onAnswer(true)}>
                Got it
              </button>
            </div>
          )}
        </>
      )}
    </article>
  );
}

export default FlashcardView;
