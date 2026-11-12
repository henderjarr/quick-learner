export type Exercise = {
  id: number;
  type: string;
  prompt: string;
};

export type AnswerResult = {
  attempt_id: number;
  is_correct: boolean;
  correct_answer: string;
  ai_feedback: string | null;
  next_review_at: string | null;
};

export type Flashcard = {
  id: number;
  term: string;
  definition: string;
  example_sentence: string | null;
  cefr_level: string | null;
  usage_note: string | null;
  part_of_speech: string | null;
  article: string | null;
  gender: string | null;
  topic: string | null;
};

// which side of the card shows first
export type Direction = "term" | "meaning";

export type Screen = "home" | "flashcards" | "exercise";

export type Progress = {
  flashcards_due: number;
  exercises_due: number;
  words_in_practice: number;
  total_words: number;
};

export type Topic = {
  topic: string;
  total_words: number;
  learning: number;
  known: number;
};
