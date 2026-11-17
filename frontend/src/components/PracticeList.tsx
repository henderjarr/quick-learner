import { useEffect, useState } from "react";
import FlashcardView from "./FlashcardView";
import { getGroupWords } from "../api";
import type { Direction, Flashcard } from "../types";

type PracticeListProps = {
  groupId: number;
  direction: Direction;
};

// practice mode: every word in one list, at your own pace.
// Nothing here touches the schedule.
function PracticeList({ groupId, direction }: PracticeListProps) {
  const [words, setWords] = useState<Flashcard[]>([]);
  const [index, setIndex] = useState(0); // which word is showing
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const data = await getGroupWords(groupId);
        if (!ignore) setWords(data);
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
  }, [groupId]);

  // derived values
  const isLast = index === words.length - 1;
  const percent =
    words.length > 0 ? Math.round(((index + 1) / words.length) * 100) : 0;

  return (
    <>
      {loading && <p className="muted">Loading the list…</p>}
      {error && <p className="error">{error}</p>}

      {words.length > 0 && (
        <>
          <div className="progress-block">
            <div className="progress">
              <div className="progress-fill" style={{ width: `${percent}%` }} />
            </div>
            <span className="progress-label">
              Card {index + 1} of {words.length} · practice only, nothing is
              scheduled
            </span>
          </div>

          {/* key={index}: a new word gets a fresh card, so it starts unflipped */}
          <FlashcardView key={index} card={words[index]} direction={direction} />

          <div className="practice-nav">
            <button onClick={() => setIndex(index - 1)} disabled={index === 0}>
              Previous
            </button>
            <button
              className="btn-primary"
              onClick={() => setIndex(isLast ? 0 : index + 1)}
            >
              {isLast ? "Start again" : "Next"}
            </button>
          </div>
        </>
      )}

      {!loading && !error && words.length === 0 && (
        <div className="card message-card">
          <h2>This list is empty</h2>
          <p className="muted">Pick another list from the dropdown.</p>
        </div>
      )}
    </>
  );
}

export default PracticeList;
