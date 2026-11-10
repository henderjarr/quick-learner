type SummaryScreenProp = {
  onHome: () => void;
  learnedWords: string[];
};

function SummaryScreen({ onHome, learnedWords }: SummaryScreenProp) {
  return (
    <section>
      <p>{learnedWords.length} words moved to practice</p>
      <ul>
        {learnedWords.map((word) => {
          return <li key={word}>{word}</li>;
        })}
      </ul>
      <p>Nice work today!</p>
      <button onClick={onHome}>Back to home</button>
    </section>
  );
}

export default SummaryScreen;
