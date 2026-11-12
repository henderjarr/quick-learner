import type { Screen } from "../types";

type NavBarProps = {
  current: Screen;
  onNavigate: (screen: Screen) => void;
};

const links: { screen: Screen; label: string }[] = [
  { screen: "home", label: "Home" },
  { screen: "flashcards", label: "Flashcards" },
  { screen: "exercise", label: "Practise" },
];

function NavBar({ current, onNavigate }: NavBarProps) {
  return (
    <nav className="navbar">
      {links.map((link) => (
        <button
          key={link.screen}
          className={link.screen === current ? "nav-link active" : "nav-link"}
          aria-current={link.screen === current ? "page" : undefined}
          onClick={() => onNavigate(link.screen)}
        >
          {link.label}
        </button>
      ))}
    </nav>
  );
}

export default NavBar;
