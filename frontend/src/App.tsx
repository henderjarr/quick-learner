import { useState } from "react";
import ExerciseScreen from "./components/ExerciseScreen";
import FlashcardScreen from "./components/FlashcardScreen";
import HomeScreen from "./components/HomeScreen";
import NavBar from "./components/NavBar";
import type { Screen } from "./types";

function App() {
  const [screen, setScreen] = useState<Screen>("home");
  // null = all topics, in the recommended order
  const [topic, setTopic] = useState<string | null>(null);

  function startFlashcards(nextTopic: string | null) {
    setTopic(nextTopic);
    setScreen("flashcards");
  }

  return (
    <>
      <header className="app-header">
        <span className="brand">Quick Learner</span>
      </header>

      <NavBar current={screen} onNavigate={setScreen} />

      <main>
        {screen === "home" && <HomeScreen onStart={startFlashcards} />}
        {screen === "flashcards" && <FlashcardScreen topic={topic} />}
        {screen === "exercise" && <ExerciseScreen />}
      </main>
    </>
  );
}

export default App;
