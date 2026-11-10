import { useState } from "react";
import ExerciseScreen from "./components/ExerciseScreen";
import type { Screen } from "./types";
import FlashcardScreen from "./components/FlashcardScreen";
import HomeScreen from "./components/HomeScreen";
import SummaryScreen from "./components/SummaryScreen";

function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const [learnedWords, setLearnedWords] = useState<string[]>([]);

  function startSession() {
    setLearnedWords([]);
    setScreen("flashcards");
  }

  return (
    <>
      <h1>Quick Learner</h1>
      {screen === "home" && <HomeScreen onStart={startSession} />}

      {screen === "flashcards" && (
        <FlashcardScreen
          onFinish={() => setScreen("exercise")}
          onLearned={(term) => setLearnedWords([...learnedWords, term])}
        />
      )}
      {screen === "exercise" && (
        <ExerciseScreen onFinish={() => setScreen("summary")} />
      )}

      {screen === "summary" && (
        <SummaryScreen
          onHome={() => setScreen("home")}
          learnedWords={learnedWords}
        />
      )}
    </>
  );
}

export default App;
