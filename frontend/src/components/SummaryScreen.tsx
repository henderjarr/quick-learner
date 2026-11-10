type SummaryScreenProp = {
  onHome: () => void;
};

function SummaryScreen({ onHome }: SummaryScreenProp) {
  return (
    <section>
      <p>Nice work today!</p>
      <button onClick={onHome}>Back to home</button>
    </section>
  );
}

export default SummaryScreen;
