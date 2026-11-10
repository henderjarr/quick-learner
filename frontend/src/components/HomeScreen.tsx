type HomeScreenProp = {
  onStart: () => void;
};

function HomeScreen({ onStart }: HomeScreenProp) {
  return (
    <section>
      <p>¡Hola! Ready for today's session?</p>
      <button onClick={onStart}>Start session</button>
    </section>
  );
}

export default HomeScreen;
