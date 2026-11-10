import type { AnswerResult, Exercise, Flashcard } from "./types";

const API_URL = "http://localhost:8000";
const USER_ID = 1;
const DOMAIN_ID = 1;

export async function generateExercise(): Promise<Exercise | undefined> {
  const response = await fetch(
    `${API_URL}/exercises/generate?user_id=${USER_ID}&domain_id=${DOMAIN_ID}`,
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
    body: JSON.stringify({ user_id: USER_ID, user_answer: userAnswer }),
  });

  if (!response.ok) {
    console.error(`Request failed: ${response.status}`);
    return;
  }

  return response.json();
}

export async function getDueFlashcards(): Promise<Flashcard[] | undefined> {
  const response = await fetch(
    `${API_URL}/flashcards/due?user_id=${USER_ID}&domain_id=${DOMAIN_ID}`,
  );

  if (!response.ok) {
    console.error(`Request failed: ${response.status}`);
    return;
  }

  return response.json();
}

export async function reviewFlashcard(
  vocabularyItemId: number,
  knewIt: boolean,
): Promise<void> {
  const response = await fetch(
    `${API_URL}/flashcards/${vocabularyItemId}/review`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID, knew_it: knewIt }),
    },
  );

  if (!response.ok) {
    console.error(`Request failed: ${response.status}`);
  }
}
