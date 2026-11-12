import { useEffect, useState } from "react";
import { getProgress, getTopics } from "../api";
import { formatTopic } from "../format";
import type { Progress, Topic } from "../types";

type HomeScreenProps = {
  onStart: (topic: string | null) => void;
};

// "24 words · 3 in progress · 5 known"
function describeTopic(t: Topic): string {
  const parts = [`${t.total_words} words`];
  if (t.known === t.total_words) {
    parts.push("all known");
  } else if (t.learning + t.known === 0) {
    parts.push("not started");
  } else {
    if (t.learning > 0) parts.push(`${t.learning} in progress`);
    if (t.known > 0) parts.push(`${t.known} known`);
  }
  return parts.join(" · ");
}

function HomeScreen({ onStart }: HomeScreenProps) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        // start both requests together, wait for both
        const [progressData, topicData] = await Promise.all([
          getProgress(),
          getTopics(),
        ]);
        if (!ignore) {
          setProgress(progressData);
          setTopics(topicData);
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

  return (
    <section className="screen">
      <div className="card">
        <h2>¡Hola!</h2>
        <p className="muted">Here is where your Spanish stands today.</p>

        {error && <p className="error">{error}</p>}

        {progress && (
          <div className="stats">
            <div className="stat">
              <span className="stat-number">{progress.flashcards_due}</span>
              <span className="stat-label">flashcards waiting</span>
            </div>
            <div className="stat">
              <span className="stat-number">{progress.exercises_due}</span>
              <span className="stat-label">words ready to practise</span>
            </div>
            <div className="stat">
              <span className="stat-number">
                {progress.words_in_practice} / {progress.total_words}
              </span>
              <span className="stat-label">words in practice</span>
            </div>
          </div>
        )}

        <button
          className="btn-primary start-button"
          onClick={() => onStart(null)}
        >
          <span className="start-title">Recommended order</span>
          <span className="start-sub">
            The most useful words first, across all topics
          </span>
        </button>
      </div>

      {topics.length > 0 && (
        <div>
          <h3>Or pick a topic</h3>
          <ul className="topic-list">
            {topics.map((t) => (
              <li key={t.topic}>
                <button className="topic-row" onClick={() => onStart(t.topic)}>
                  <span className="topic-name">{formatTopic(t.topic)}</span>
                  <span className="muted small">{describeTopic(t)}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default HomeScreen;
