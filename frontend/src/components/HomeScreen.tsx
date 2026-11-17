import { useEffect, useState } from "react";
import { getGroups, getProgress } from "../api";
import ListSelect from "./ListSelect";
import type { Group, Progress } from "../types";

type HomeScreenProps = {
  onStart: (groupId: number | null) => void;
  onPractise: () => void;
};

function HomeScreen({ onStart, onPractise }: HomeScreenProps) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [groups, setGroups] = useState<Group[]>([]);
  const [selected, setSelected] = useState<number | null>(null); // null = learning path
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        // start both requests together, wait for both
        const [progressData, groupData] = await Promise.all([
          getProgress(),
          getGroups(),
        ]);
        if (!ignore) {
          setProgress(progressData);
          setGroups(groupData);
        }
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

  // derived values for the progress card and the Practise button
  const percent =
    progress && progress.total_words > 0
      ? Math.round((progress.words_in_practice / progress.total_words) * 100)
      : 0;
  const ready = progress?.exercises_due ?? 0;
  const practiseLabel =
    ready > 0 ? `Practise ${ready} ${ready === 1 ? "word" : "words"}` : "Practise";

  return (
    <>
      <div className="page-header">
        <div>
          <h1>¡Hola!</h1>
          <p className="muted">Here is where your Spanish stands today.</p>
        </div>
      </div>

      {error && <p className="error">{error}</p>}

      {progress && (
        <section className="card" aria-label="Progress">
          <div className="stats">
            <div className="stat">
              <span className="stat-number">{progress.flashcards_due}</span>
              <span className="stat-label">flashcards waiting</span>
            </div>
            <div className="stat">
              <span className="stat-number">{progress.exercises_due}</span>
              <span className="stat-label">words ready to practise</span>
            </div>
          </div>
          <div className="progress-block">
            <div className="progress-label-row">
              <strong>Words in practice</strong>
              <span className="muted">
                {progress.words_in_practice} of {progress.total_words}
              </span>
            </div>
            <div className="progress">
              <div className="progress-fill" style={{ width: `${percent}%` }} />
            </div>
          </div>
        </section>
      )}

      <section className="card" aria-label="Flashcards">
        <div className="card-head">
          <div className="icon-tile">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="6" width="14" height="14" rx="2" />
              <path d="M7 2h12a2 2 0 0 1 2 2v12" />
            </svg>
          </div>
          <div className="card-head-text">
            <h2>Flashcards</h2>
            <p className="muted">
              Follow the learning path, or practise any list at your own pace.
            </p>
          </div>
        </div>
        <div className="controls">
          <div className="field field-grow">
            <label htmlFor="home-list" className="field-label">
              List
            </label>
            <ListSelect
              id="home-list"
              groups={groups}
              value={selected}
              onChange={setSelected}
            />
          </div>
          <button className="btn-primary" onClick={() => onStart(selected)}>
            {selected === null ? "Start learning path" : "Practise this list"}
          </button>
        </div>
      </section>

      <section className="card" aria-label="Practise">
        <div className="card-head">
          <div className="icon-tile">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
            </svg>
          </div>
          <div className="card-head-text">
            <h2>Practise</h2>
            <p className="muted">
              The AI writes a sentence for each word you know.
            </p>
          </div>
          <button onClick={onPractise}>{practiseLabel}</button>
        </div>
      </section>

      <section className="how-it-works" aria-label="How it works">
        <h3 className="eyebrow">How it works</h3>
        <ol className="steps">
          <li>
            <span className="step-number">1</span>
            <span>
              <strong>Flashcards.</strong> Meet a few new words at a time.
            </span>
          </li>
          <li>
            <span className="step-number">2</span>
            <span>
              <strong>Practise.</strong> Fill the blank in a sentence the AI
              writes.
            </span>
          </li>
          <li>
            <span className="step-number">3</span>
            <span>
              <strong>Review.</strong> Code grades your answer and schedules
              the next review.
            </span>
          </li>
        </ol>
      </section>
    </>
  );
}

export default HomeScreen;
