import { useEffect, useState } from "react";
import FlashcardView from "./FlashcardView";
import { dealMoreCards, getDueFlashcards, reviewFlashcard } from "../api";
import type { Direction, Flashcard } from "../types";

type Mode = "new" | "known";
type LearningPileProps = {
  direction: Direction;
};

// the learning path: the schedule decides which cards come up
function LearningPile({ direction }: LearningPileProps) {
  const [mode, setMode] = useState<Mode>("new");
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [total, setTotal] = useState(0); // how many cards we started with
  const [reviewCount, setReviewCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dealing, setDealing] = useState(false); // true while "Deal 10 more" runs
  const [notice, setNotice] = useState<string | null>(null); // e.g. "No new words left"

  // load the pile when it appears, and again whenever the mode changes
  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const data = await getDueFlashcards(mode === "known");
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
  }, [mode]);

  function changeMode(next: Mode) {
    if (next === mode) return;
    // clear the old pile, then the effect above loads the new one
    setCards([]);
    setTotal(0);
    setError(null);
    setNotice(null);
    setLoading(true);
    setMode(next);
  }

  async function handleDeal() {
    setDealing(true);
    setError(null);
    setNotice(null);
    try {
      const newCards = await dealMoreCards();
      if (newCards.length === 0) {
        setNotice("No new words left.");
      } else {
        // add to the end of the pile; total grows so the progress bar stays honest
        setCards([...cards, ...newCards]);
        setTotal(total + newCards.length);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setDealing(false);
    }
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
    <>
      <div className="pile-bar">
        <div className="segmented" role="group" aria-label="Cards">
          <button
            className={mode === "new" ? "active" : ""}
            aria-pressed={mode === "new"}
            onClick={() => changeMode("new")}
          >
            New
          </button>
          <button
            className={mode === "known" ? "active" : ""}
            aria-pressed={mode === "known"}
            onClick={() => changeMode("known")}
          >
            Known
          </button>
        </div>
        {cards.length > 0 && (
          <span className="muted small">{cards.length} cards left</span>
        )}
      </div>

      {mode === "new" && total > 0 && (
        <div className="progress-block">
          <div className="progress">
            <div className="progress-fill" style={{ width: `${percent}%` }} />
          </div>
          <span className="progress-label">
            {learned} of {total} moved to practice
          </span>
        </div>
      )}

      {mode === "known" && cards.length > 0 && (
        <span className="progress-label">
          Card {learned + 1} of {total}
        </span>
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
        <div className="card message-card">
          <h2>{total > 0 ? "All cards done!" : "No new words left"}</h2>
          <p className="muted">
            {total > 0
              ? "These words are ready to practise in sentences. Open the Practise tab when you like."
              : "You have started every word. Review your known words, or practise them in sentences."}
          </p>
        </div>
      )}

      {finished && mode === "known" && total > 0 && (
        <div className="card message-card">
          <h2>That's all of them!</h2>
          <p className="muted">You have been through every known word.</p>
        </div>
      )}

      {finished && mode === "known" && total === 0 && (
        <div className="card message-card">
          <h2>No known words yet</h2>
          <p className="muted">
            Learn a few first, then come back to review them.
          </p>
          <button className="btn-primary" onClick={() => changeMode("new")}>
            Show new words
          </button>
        </div>
      )}

      {mode === "new" && !loading && (
        <div className="deal-row">
          <button className="btn-ghost" onClick={handleDeal} disabled={dealing}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 5v14" />
              <path d="M5 12h14" />
            </svg>
            {dealing ? "Dealing…" : "Deal 10 more"}
          </button>
          {notice && <p className="muted small">{notice}</p>}
        </div>
      )}
    </>
  );
}

export default LearningPile;
