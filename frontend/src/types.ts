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
