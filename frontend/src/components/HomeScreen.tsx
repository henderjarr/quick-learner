import { useEffect, useState } from "react";
import { getProgress } from "../api";
import type { Progress } from "../types";

type HomeScreenProp = {
  onStart: () => void;
};

function HomeScreen({ onStart }: HomeScreenProp) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const data = await getProgress();
        if (!ignore) setProgress(data);
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Something went wrong");
        }
      }
    }

    load();
    return () => {
      ignore = true; // cleanup: Home went away, ignore late responses
    };
  }, []);

  return (
    <section>
      {error && <p>{error}</p>}

      {progress && (
        <>
          <p>{progress.exercises_due} exercises due</p>
          <p>{progress.flashcards_due} flashcards due</p>
          <p>
            {progress.words_in_practice} / {progress.total_words} words in
            practice
          </p>
        </>
      )}
      <p>¡Hola! Ready for today's session?</p>
      <button onClick={onStart}>Start session</button>
    </section>
  );
}

export default HomeScreen;
