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

// "Bebo un ___ (coffee)." -> the ___ is drawn as a line
function Sentence({ text }: { text: string }) {
  const parts = text.split("___");
  if (parts.length !== 2) return <>{text}</>; // no blank (or several): plain text
  return (
    <>
      {parts[0]}
      <span className="blank">
        <span className="sr-only">blank</span>
      </span>
      {parts[1]}
    </>
  );
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
    <>
      <div className="page-header">
        <h1>Practise</h1>
        {skipped.length > 0 && (
          <span className="muted small">{skipped.length} skipped</span>
        )}
      </div>

      {loading && <p className="muted">Your AI tutor is writing a sentence…</p>}
      {error && <p className="error">{error}</p>}

      {exercise && (
        <article className="card exercise" aria-label="Exercise">
          <div className="exercise-head">
            <span className="eyebrow">Fill in the blank</span>
            <p className="exercise-prompt">
              <Sentence text={exercise.prompt} />
            </p>
          </div>

          <form
            className="field"
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
          >
            <label htmlFor="ex-answer" className="field-label">
              Your answer
            </label>
            <div className="answer-row">
              <input
                id="ex-answer"
                className="exercise-input"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type the missing word"
                disabled={result !== null}
                autoComplete="off"
                autoFocus
              />
              {result === null && (
                <>
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={checking || answer.trim() === ""}
                  >
                    Check
                  </button>
                  <button
                    type="button"
                    onClick={handleSkip}
                    disabled={checking}
                  >
                    Skip
                  </button>
                </>
              )}
            </div>
          </form>

          {checking && (
            <p className="muted">Your tutor is reading your answer…</p>
          )}

          {result && (
            <div className={result.is_correct ? "result correct" : "result learning"}>
              <p className="result-title">
                {result.is_correct ? "Correct!" : "Still learning"}
              </p>
              <p>
                The answer is <strong>{result.correct_answer}</strong>.
              </p>
              {result.next_review_at && (
                <p className="muted small">
                  Next review: {formatReviewDate(result.next_review_at)}
                </p>
              )}
            </div>
          )}

          {result?.ai_feedback && (
            <section className="tutor" aria-label="AI tutor">
              <div className="tutor-head">
                <span className="eyebrow">AI tutor</span>
                <span className="muted small">
                  Graded by code, explained by AI
                </span>
              </div>
              <p>{result.ai_feedback}</p>
            </section>
          )}

          {result && (
            <div className="card-footer">
              <button className="btn-primary" onClick={handleNext}>
                Next sentence
              </button>
            </div>
          )}
        </article>
      )}

      {nothingReady && (
        <div className="card message-card">
          <h2>Nothing to practise right now</h2>
          <p className="muted">
            {skipped.length > 0
              ? "You skipped the rest. Try them again, or learn some new words."
              : "Words appear here after you mark them “Got it” on Flashcards."}
          </p>
          <div className="centered-row">
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
    </>
  );
}

export default ExerciseScreen;
