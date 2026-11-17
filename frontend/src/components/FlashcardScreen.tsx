import { useEffect, useState } from "react";
import LearningPile from "./LearningPile";
import ListSelect from "./ListSelect";
import PracticeList from "./PracticeList";
import { getGroups } from "../api";
import type { Direction, Group } from "../types";

type FlashcardScreenProps = {
  groupId: number | null; // null = the learning path
  onGroupChange: (groupId: number | null) => void; // the choice lives in App
};

// the parent: title, list dropdown, direction toggle.
// It shows the learning path OR one practice list; each child keeps its own state.
function FlashcardScreen({ groupId, onGroupChange }: FlashcardScreenProps) {
  const [direction, setDirection] = useState<Direction>("term");
  const [groups, setGroups] = useState<Group[]>([]);

  // the lists for the dropdown: load once
  useEffect(() => {
    let ignore = false;
    getGroups()
      .then((data) => {
        if (!ignore) setGroups(data);
      })
      .catch(() => {
        // the dropdown still works with just the learning path
      });
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <>
      <div className="page-header">
        <h1>Flashcards</h1>
      </div>

      <div className="controls">
        <div className="field field-grow">
          <label htmlFor="fc-list" className="field-label">
            List
          </label>
          <ListSelect
            id="fc-list"
            groups={groups}
            value={groupId}
            onChange={onGroupChange}
          />
        </div>

        <div className="field">
          <span id="fc-direction" className="field-label">
            Show first
          </span>
          <div
            className="segmented"
            role="group"
            aria-labelledby="fc-direction"
          >
            <button
              className={direction === "term" ? "active" : ""}
              aria-pressed={direction === "term"}
              onClick={() => setDirection("term")}
            >
              Spanish
            </button>
            <button
              className={direction === "meaning" ? "active" : ""}
              aria-pressed={direction === "meaning"}
              onClick={() => setDirection("meaning")}
            >
              English
            </button>
          </div>
        </div>
      </div>

      {/* key={groupId}: switching lists gives a fresh PracticeList (index back to 0) */}
      {groupId === null ? (
        <LearningPile direction={direction} />
      ) : (
        <PracticeList key={groupId} groupId={groupId} direction={direction} />
      )}
    </>
  );
}

export default FlashcardScreen;
