import { useState } from "react";
import ExerciseScreen from "./components/ExerciseScreen";
import FlashcardScreen from "./components/FlashcardScreen";
import HomeScreen from "./components/HomeScreen";
import NavBar from "./components/NavBar";
import type { Screen } from "./types";

function App() {
  const [screen, setScreen] = useState<Screen>("home");
  // which list Flashcards shows: a group id, or null = the learning path
  const [groupId, setGroupId] = useState<number | null>(null);

  function startFlashcards(nextGroupId: number | null) {
    setGroupId(nextGroupId);
    setScreen("flashcards");
  }

  return (
    <>
      <header className="app-header">
        <div className="container header-inner">
          <span className="brand">Quick Learner</span>
          <span className="chip">Spanish · A1</span>
          <NavBar current={screen} onNavigate={setScreen} />
        </div>
      </header>

      <main className="container page">
        {screen === "home" && (
          <HomeScreen
            onStart={startFlashcards}
            onPractise={() => setScreen("exercise")}
          />
        )}
        {screen === "flashcards" && (
          <FlashcardScreen groupId={groupId} onGroupChange={setGroupId} />
        )}
        {screen === "exercise" && (
          <ExerciseScreen onGoToFlashcards={() => startFlashcards(null)} />
        )}
      </main>
    </>
  );
}

export default App;
