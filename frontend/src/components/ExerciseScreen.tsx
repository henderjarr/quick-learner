import { useEffect, useState } from "react";

import { generateExercise, submitAnswer } from "../api";
import type { AnswerResult, Exercise } from "../types";

type ExerciseScreenProps = {
  onGoToFlashcards: () => void;
};

// the backend sends UTC times without a timezone, so add "Z" before parsing
function formatReviewDate(isoString: string): string {
  const date = new Date(isoString + "Z");
  return date.toLocaleDateString(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function ExerciseScreen({ onGoToFlashcards }: ExerciseScreenProps) {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [loading, setLoading] = useState(true); // a sentence loads on arrival
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skipped, setSkipped] = useState<number[]>([]); // word ids skipped this visit
  const [round, setRound] = useState(0); // +1 = "load the next sentence"

  // load a sentence on arrival, and again whenever skipped or round changes
  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const data = await generateExercise(skipped);
        if (!ignore) setExercise(data); // null = nothing ready
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
  }, [skipped, round]);

  // clear the old sentence before the effect loads a new one
  function clearForNextLoad() {
    setExercise(null);
    setAnswer("");
    setResult(null);
    setError(null);
    setLoading(true);
  }

  function handleSkip() {
    if (!exercise) return;
    clearForNextLoad();
    setSkipped([...skipped, exercise.vocabulary_item_id]);
  }

  function handleNext() {
    clearForNextLoad();
    setRound(round + 1);
  }

  function handleRetrySkipped() {
    clearForNextLoad();
    setSkipped([]);
  }

  async function handleSubmit() {
    if (!exercise || answer.trim() === "") return;
    setChecking(true);
    setError(null);
    try {
      const data = await submitAnswer(exercise.id, answer);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setChecking(false);
    }
  }

  // derived value: loaded, no error, and the backend had nothing for us
  const nothingReady = !loading && !error && exercise === null;

  return (
    <section className="screen">
      <div className="screen-header">
        <h2>Practise</h2>
        {skipped.length > 0 && (
          <span className="muted small">{skipped.length} skipped</span>
        )}
      </div>

      {loading && <p className="muted">Your AI tutor is writing a sentence…</p>}
      {error && <p className="error">{error}</p>}

      {exercise && (
        <div className="card">
          <p className="exercise-prompt">{exercise.prompt}</p>

          <form
            className="exercise-form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
          >
            <input
              className="exercise-input"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type the missing word"
              disabled={result !== null}
              autoFocus
            />
            {result === null ? (
              <>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={checking || answer.trim() === ""}
                >
                  Check
                </button>
                <button type="button" onClick={handleSkip} disabled={checking}>
                  Skip
                </button>
              </>
            ) : (
              <button type="button" className="btn-primary" onClick={handleNext}>
                Next
              </button>
            )}
          </form>

          {checking && <p className="muted">Your tutor is reading your answer…</p>}

          {result && (
            <div
              className={
                result.is_correct
                  ? "exercise-result correct"
                  : "exercise-result learning"
              }
            >
              <p className="exercise-verdict">
                {result.is_correct ? "Correct!" : "Still learning"}
              </p>
              <p>
                Answer: <strong>{result.correct_answer}</strong>
              </p>
              {result.next_review_at && (
                <p className="muted small">
                  Next review: {formatReviewDate(result.next_review_at)}
                </p>
              )}
            </div>
          )}

          {result?.ai_feedback && (
            <div className="tutor-panel">
              <p className="tutor-label">Graded by code, explained by AI</p>
              <p>{result.ai_feedback}</p>
            </div>
          )}
        </div>
      )}

      {nothingReady && (
        <div className="card">
          <h2>Nothing to practise right now</h2>
          <p className="muted">
            {skipped.length > 0
              ? "You skipped the rest. Try them again, or learn some new words."
              : "Words appear here after you mark them “Got it” on Flashcards."}
          </p>
          <div className="exercise-actions">
            {skipped.length > 0 && (
              <button className="btn-primary" onClick={handleRetrySkipped}>
                Try the skipped ones again
              </button>
            )}
            <button
              className={skipped.length > 0 ? "" : "btn-primary"}
              onClick={onGoToFlashcards}
            >
              Go to Flashcards
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

export default ExerciseScreen;
