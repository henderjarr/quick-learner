import { useState } from "react";
import ExerciseScreen from "./components/ExerciseScreen";
import type { Screen } from "./types";
import FlashcardScreen from "./components/FlashcardScreen";
import HomeScreen from "./components/HomeScreen";
import SummaryScreen from "./components/SummaryScreen";

function App() {
  const [screen, setScreen] = useState<Screen>("home");

  return (
    <>
      <h1>Quick Learner</h1>
      {screen === "home" && (
        <HomeScreen onStart={() => setScreen("flashcards")} />
      )}

      {screen === "flashcards" && (
        <FlashcardScreen onFinish={() => setScreen("exercise")} />
      )}
      {screen === "exercise" && (
        <ExerciseScreen onFinish={() => setScreen("summary")} />
      )}

      {screen === "summary" && (
        <SummaryScreen onHome={() => setScreen("home")} />
      )}
    </>
  );
}

export default App;
