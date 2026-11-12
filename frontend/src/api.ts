import type {
  AnswerResult,
  Exercise,
  Flashcard,
  Progress,
  Topic,
} from "./types";

const API_URL = "http://localhost:8000";
const USER_ID = 1;
const DOMAIN_ID = 1;

// helper function: error collector
async function throwIfNotOk(response: Response) {
  if (response.ok) return;

  let message = `Request failed (${response.status})`;
  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      message = body.detail;
    }
  } catch {
    // the body wasn't JSON, so keep the default message
  }
  throw new Error(message);
}

// -------------------------------

export async function generateExercise(): Promise<Exercise> {
  const response = await fetch(
    `${API_URL}/exercises/generate?user_id=${USER_ID}&domain_id=${DOMAIN_ID}`,
    { method: "POST" },
  );

  await throwIfNotOk(response);

  return response.json();
}

export async function submitAnswer(
  exerciseId: number,
  userAnswer: string,
): Promise<AnswerResult> {
  const response = await fetch(`${API_URL}/exercises/${exerciseId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: USER_ID, user_answer: userAnswer }),
  });

  await throwIfNotOk(response);

  return response.json();
}

export async function getDueFlashcards(
  known = false,
  topic?: string,
): Promise<Flashcard[]> {
  const params = new URLSearchParams({
    user_id: String(USER_ID),
    domain_id: String(DOMAIN_ID),
  });
  if (known) params.set("known", "true");
  if (topic) params.set("topic", topic);

  const response = await fetch(`${API_URL}/flashcards/due?${params}`);

  await throwIfNotOk(response);

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

  await throwIfNotOk(response);
}

export async function getProgress(): Promise<Progress> {
  const response = await fetch(
    `${API_URL}/progress?user_id=${USER_ID}&domain_id=${DOMAIN_ID}`,
  );

  await throwIfNotOk(response);

  return response.json();
}

export async function getTopics(): Promise<Topic[]> {
  const params = new URLSearchParams({
    user_id: String(USER_ID),
    domain_id: String(DOMAIN_ID),
  });
  const response = await fetch(`${API_URL}/topics?${params}`);

  await throwIfNotOk(response);

  return response.json();
}
