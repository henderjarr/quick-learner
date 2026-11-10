import { useState } from "react";

import { generateExercise, submitAnswer } from "../api";
import type { AnswerResult, Exercise } from "../types";

type ExerciseScreenProps = {
  onFinish: () => void;
};

function ExerciseScreen({ onFinish }: ExerciseScreenProps) {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);

  async function handleGenerate() {
    setLoading(true);
    setError(null); // clear any old error
    try {
      const data = await generateExercise();
      setExercise(data);
      setAnswer("");
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    if (!exercise) return;
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

  return (
    <section>
      <button onClick={handleGenerate} disabled={loading}>
        Generate exercise
      </button>
      {loading && <p>Your AI tutor is writing a sentence…</p>}
      {error && <p>{error}</p>}
      {exercise && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <p>{exercise.prompt}</p>
          <input value={answer} onChange={(e) => setAnswer(e.target.value)} />
          <button type="submit" disabled={checking || result !== null}>
            Check answer
          </button>
        </form>
      )}
      {checking && <p>Your tutor is reading your answer…</p>}

      {result && (
        <div>
          <p>
            {result.is_correct
              ? "Correct!"
              : `Still learning. The answer is: ${result.correct_answer}`}
          </p>
          {result.ai_feedback && <p>{result.ai_feedback}</p>}
        </div>
      )}
      <button onClick={onFinish}>Finish session</button>
    </section>
  );
}

export default ExerciseScreen;
