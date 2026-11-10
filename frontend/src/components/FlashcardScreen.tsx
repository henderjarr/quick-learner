import { useState } from "react";
import FlashcardView from "./FlashcardView";
import { getDueFlashcards, reviewFlashcard } from "../api";
import type { Flashcard } from "../types";

type FlashcardScreenProps = {
  onFinish: () => void;
};

function FlashcardScreen({ onFinish }: FlashcardScreenProps) {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [reviewCount, setReviewCount] = useState(0);

  async function handleFlashcardAnswer(knewIt: boolean) {
    const card = cards[0];
    await reviewFlashcard(card.id, knewIt);

    const rest = cards.slice(1);
    if (knewIt) {
      setCards(rest); // done with this word for now
    } else {
      setCards([...rest, card]); // back of the pile, comes round again
    }
    setReviewCount(reviewCount + 1);
  }

  async function handleLoadFlashcards() {
    const data = await getDueFlashcards();
    if (data) {
      setCards(data);
    }
  }

  return (
    <section>
      <button onClick={handleLoadFlashcards}>Load flashcards</button>
      {cards.length > 0 && (
        <>
          <p>{cards.length} cards left</p>
          <FlashcardView
            key={reviewCount}
            card={cards[0]}
            onAnswer={handleFlashcardAnswer}
          />
        </>
      )}

      <button onClick={onFinish}>Practise these words</button>
    </section>
  );
}

export default FlashcardScreen;
