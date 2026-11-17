import type { ReactNode } from "react";
import type { Screen } from "../types";

type NavBarProps = {
  current: Screen;
  onNavigate: (screen: Screen) => void;
};

// small line icons; CSS only shows them on phones (bottom bar)
function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      className="nav-icon"
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const links: { screen: Screen; label: string; icon: ReactNode }[] = [
  {
    screen: "home",
    label: "Home",
    icon: (
      <Icon>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
      </Icon>
    ),
  },
  {
    screen: "flashcards",
    label: "Flashcards",
    icon: (
      <Icon>
        <rect x="3" y="6" width="14" height="14" rx="2" />
        <path d="M7 2h12a2 2 0 0 1 2 2v12" />
      </Icon>
    ),
  },
  {
    screen: "exercise",
    label: "Practise",
    icon: (
      <Icon>
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
      </Icon>
    ),
  },
];

function NavBar({ current, onNavigate }: NavBarProps) {
  return (
    <nav className="navbar" aria-label="Main">
      {links.map((link) => (
        <button
          key={link.screen}
          className={link.screen === current ? "nav-link active" : "nav-link"}
          aria-current={link.screen === current ? "page" : undefined}
          onClick={() => onNavigate(link.screen)}
        >
          {link.icon}
          {link.label}
        </button>
      ))}
    </nav>
  );
}

export default NavBar;
