import { useState } from "react";

import { generateExercise, submitAnswer } from "../api";
import type { AnswerResult, Exercise } from "../types";

type ExerciseScreenProps = {
  onFinish: () => void;
};

function ExerciseScreen({ onFinish }: ExerciseScreenProps) {
  // 1. state goes here
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<AnswerResult | null>(null);

  // 2. handler functions go here
  async function handleGenerate() {
    const data = await generateExercise();
    if (data) {
      setExercise(data);
      setAnswer("");
      setResult(null);
    }
  }

  async function handleSubmit() {
    if (!exercise) return;
    const data = await submitAnswer(exercise.id, answer);
    if (data) {
      setResult(data);
    }
  }

  return (
    <section>
      <button onClick={handleGenerate}>Generate exercise</button>

      {exercise && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <p>{exercise.prompt}</p>
          <input value={answer} onChange={(e) => setAnswer(e.target.value)} />
          <button type="submit" disabled={result !== null}>
            Check answer
          </button>
        </form>
      )}

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
