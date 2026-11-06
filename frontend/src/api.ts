import type { AnswerResult, Exercise } from "./types";

const API_URL = "http://localhost:8000";

export async function generateExercise(): Promise<Exercise | undefined> {
  const response = await fetch(
    `${API_URL}/exercises/generate?user_id=1&domain_id=1`,
    { method: "POST" },
  );

  if (!response.ok) {
    console.error(`Request failed: ${response.status}`);
    return;
  }

  return response.json();
}

export async function submitAnswer(
  exerciseId: number,
  userAnswer: string,
): Promise<AnswerResult | undefined> {
  const response = await fetch(`${API_URL}/exercises/${exerciseId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: 1, user_answer: userAnswer }),
  });

  if (!response.ok) {
    console.error(`Request failed: ${response.status}`);
    return;
  }

  return response.json();
}
