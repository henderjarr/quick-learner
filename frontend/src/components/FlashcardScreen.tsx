import { useEffect, useState } from "react";
import FlashcardView from "./FlashcardView";
import { formatTopic } from "../format";
import { getDueFlashcards, reviewFlashcard } from "../api";
import type { Direction, Flashcard } from "../types";

type Mode = "new" | "known";
type FlashcardScreenProps = {
  topic: string | null;
};

function FlashcardScreen({ topic }: FlashcardScreenProps) {
  const [mode, setMode] = useState<Mode>("new");
  const [direction, setDirection] = useState<Direction>("term");
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [total, setTotal] = useState(0); // how many cards we started with
  const [reviewCount, setReviewCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // load the cards when the screen appears, and again whenever the mode changes
  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const data = await getDueFlashcards(
          mode === "known",
          topic ?? undefined,
        );
        if (!ignore) {
          setCards(data);
          setTotal(data.length);
        }
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Something went wrong");
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [mode, topic]);

  function changeMode(next: Mode) {
    if (next === mode) return;
    // clear the old pile, then the effect above loads the new one
    setCards([]);
    setTotal(0);
    setError(null);
    setLoading(true);
    setMode(next);
  }

  async function handleFlashcardAnswer(knewIt: boolean) {
    const card = cards[0];
    const rest = cards.slice(1);
    setError(null);
    try {
      if (mode === "known") {
        // "Got it" changes nothing. "Still learning" moves the word
        // back to the flashcard pile. Either way, on to the next card.
        if (!knewIt) await reviewFlashcard(card.id, false);
        setCards(rest);
      } else {
        await reviewFlashcard(card.id, knewIt);
        // "Still learning" goes to the back of the pile and comes round again
        setCards(knewIt ? rest : [...rest, card]);
      }
      setReviewCount(reviewCount + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  // derived values: calculated from state, not stored in state
  const learned = total - cards.length;
  const percent = total > 0 ? Math.round((learned / total) * 100) : 0;
  const finished = !loading && !error && cards.length === 0;

  return (
    <section className="screen">
      <div className="screen-header">
        <h2>{topic ? formatTopic(topic) : "All topics"}</h2>
        {cards.length > 0 && (
          <span className="muted small">{cards.length} cards left</span>
        )}
      </div>

      <div className="toggles">
        <div className="toggle">
          <button
            className={mode === "new" ? "active" : ""}
            aria-pressed={mode === "new"}
            onClick={() => changeMode("new")}
          >
            New words
          </button>
          <button
            className={mode === "known" ? "active" : ""}
            aria-pressed={mode === "known"}
            onClick={() => changeMode("known")}
          >
            Known words
          </button>
        </div>

        <div className="toggle">
          <button
            className={direction === "term" ? "active" : ""}
            aria-pressed={direction === "term"}
            onClick={() => setDirection("term")}
          >
            Spanish first
          </button>
          <button
            className={direction === "meaning" ? "active" : ""}
            aria-pressed={direction === "meaning"}
            onClick={() => setDirection("meaning")}
          >
            English first
          </button>
        </div>
      </div>

      {mode === "new" && total > 0 && (
        <div>
          <div className="progress">
            <div className="progress-fill" style={{ width: `${percent}%` }} />
          </div>
          <p className="muted small">
            {learned} of {total} moved to practice
          </p>
        </div>
      )}

      {mode === "known" && cards.length > 0 && (
        <p className="muted small">
          Card {learned + 1} of {total}
        </p>
      )}

      {loading && <p className="muted">Loading your cards…</p>}
      {error && <p className="error">{error}</p>}

      {cards.length > 0 && (
        <FlashcardView
          key={reviewCount}
          card={cards[0]}
          direction={direction}
          onAnswer={handleFlashcardAnswer}
        />
      )}

      {finished && mode === "new" && (
        <div className="card flashcard">
          <h2>{total > 0 ? "All cards done!" : "No new words left"}</h2>
          <p className="muted">
            {total > 0
              ? "These words are ready to practise in sentences. Open the Practise tab when you like."
              : "You have started every word here. Review your known words, or practise them in sentences."}
          </p>
        </div>
      )}

      {finished && mode === "known" && total > 0 && (
        <div className="card flashcard">
          <h2>That's all of them!</h2>
          <p className="muted">You have been through every known word.</p>
        </div>
      )}

      {finished && mode === "known" && total === 0 && (
        <div className="card flashcard">
          <h2>No known words yet</h2>
          <p className="muted">
            Learn a few first, then come back to review them.
          </p>
          <button className="btn-primary" onClick={() => changeMode("new")}>
            Show new words
          </button>
        </div>
      )}
    </section>
  );
}

export default FlashcardScreen;
