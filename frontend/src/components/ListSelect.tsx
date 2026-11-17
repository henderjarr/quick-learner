import type { Group } from "../types";

type ListSelectProps = {
  id: string; // links the <label htmlFor> to this select
  groups: Group[];
  value: number | null; // a group id, or null = the learning path
  onChange: (groupId: number | null) => void;
};

// the list dropdown, shared by Home and Flashcards:
// the learning path first, then the practice lists under two sub-headings
function ListSelect({ id, groups, value, onChange }: ListSelectProps) {
  const topics = groups.filter((g) => g.kind === "topic");
  const grammar = groups.filter((g) => g.kind === "grammar");

  return (
    <div className="select-wrap">
      <select
        id={id}
        className="select"
        // a <select> value is always a string, so "" stands for the learning path
        value={value === null ? "" : String(value)}
        onChange={(e) =>
          onChange(e.target.value === "" ? null : Number(e.target.value))
        }
      >
        <option value="">Learning path (recommended)</option>
        {/* <optgroup> = a sub-heading inside a dropdown */}
        <optgroup label="Practice topics">
          {topics.map((g) => (
            <option key={g.id} value={g.id}>
              {`${g.name} · ${g.word_count} words`}
            </option>
          ))}
        </optgroup>
        <optgroup label="Grammar">
          {grammar.map((g) => (
            <option key={g.id} value={g.id}>
              {`${g.name} · ${g.word_count} words`}
            </option>
          ))}
        </optgroup>
      </select>
      <svg
        className="select-chevron"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </div>
  );
}

export default ListSelect;
