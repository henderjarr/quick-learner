import { useState } from "react";
import type { Flashcard } from "../types";

type FlashcardViewProps = {
  card: Flashcard;
  onAnswer: (knewIt: boolean) => void;
};

function FlashcardView({ card, onAnswer }: FlashcardViewProps) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className="flashcard">
      <h2>{card.term}</h2>

      {!flipped ? (
        <button onClick={() => setFlipped(true)}>Show meaning</button>
      ) : (
        <>
          <p>{card.definition}</p>
          {card.example_sentence && <p>{card.example_sentence}</p>}
          <button onClick={() => onAnswer(false)}>Still learning</button>
          <button onClick={() => onAnswer(true)}>Got it</button>
        </>
      )}
    </div>
  );
}

export default FlashcardView;
