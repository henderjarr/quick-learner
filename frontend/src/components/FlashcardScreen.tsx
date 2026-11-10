import { useState } from "react";
import FlashcardView from "./FlashcardView";
import { getDueFlashcards, reviewFlashcard } from "../api";
import type { Flashcard } from "../types";

type FlashcardScreenProps = {
  onFinish: () => void;
  onLearned: (term: string) => void;
};

function FlashcardScreen({ onFinish, onLearned }: FlashcardScreenProps) {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [reviewCount, setReviewCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLoadFlashcards() {
    setLoading(true);
    setError(null);
    try {
      const data = await getDueFlashcards();
      setCards(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleFlashcardAnswer(knewIt: boolean) {
    const card = cards[0];
    setError(null);
    try {
      await reviewFlashcard(card.id, knewIt);

      // only reached if the backend saved the review
      const rest = cards.slice(1);
      if (knewIt) {
        setCards(rest);
        onLearned(card.term);
      } else {
        setCards([...rest, card]); // back of the pile, comes round again
      }
      setReviewCount(reviewCount + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <section>
      <button onClick={handleLoadFlashcards} disabled={loading}>
        Load flashcards
      </button>
      {loading && <p>Loading your cards…</p>}
      {error && <p>{error}</p>}

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
