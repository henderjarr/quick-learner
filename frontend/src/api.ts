import type {
  AnswerResult,
  Exercise,
  Flashcard,
  Group,
  Progress,
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

// returns null when no exercise is ready (the backend sends a 404)
export async function generateExercise(
  excludeIds: number[] = [],
): Promise<Exercise | null> {
  const params = new URLSearchParams({
    user_id: String(USER_ID),
    domain_id: String(DOMAIN_ID),
  });
  // append (not set): "exclude" can appear many times in the URL
  for (const id of excludeIds) {
    params.append("exclude", String(id));
  }

  const response = await fetch(`${API_URL}/exercises/generate?${params}`, {
    method: "POST",
  });

  if (response.status === 404) return null;
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

// the learning path pile (known = true: every word already moved to practice)
export async function getDueFlashcards(known = false): Promise<Flashcard[]> {
  const params = new URLSearchParams({
    user_id: String(USER_ID),
    domain_id: String(DOMAIN_ID),
  });
  if (known) params.set("known", "true");

  const response = await fetch(`${API_URL}/flashcards/due?${params}`);

  await throwIfNotOk(response);

  return response.json();
}

// starts 10 new words and returns them; an empty list = none left
export async function dealMoreCards(): Promise<Flashcard[]> {
  const params = new URLSearchParams({
    user_id: String(USER_ID),
    domain_id: String(DOMAIN_ID),
  });

  const response = await fetch(`${API_URL}/flashcards/deal?${params}`, {
    method: "POST",
  });

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

// every list (topics and grammar groups) with its word count
export async function getGroups(): Promise<Group[]> {
  const response = await fetch(`${API_URL}/groups?domain_id=${DOMAIN_ID}`);

  await throwIfNotOk(response);

  return response.json();
}

// every word in one list, for practice mode
export async function getGroupWords(groupId: number): Promise<Flashcard[]> {
  const response = await fetch(`${API_URL}/groups/${groupId}/words`);

  await throwIfNotOk(response);

  return response.json();
}
