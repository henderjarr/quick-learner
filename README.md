# Quick Learner

A Spanish vocabulary app (A1, Castilian Spanish, 636 words) that uses generative AI to write practice sentences and explain mistakes. The learner stays in control: they choose the topic, the card direction, and whether to learn new words or review known ones.

Built for the MSIT "AI for Developers" course.

## How GenAI is used

All AI calls live in one file, [`backend/ai_service.py`](backend/ai_service.py), behind a single `chat()` function that works with **OpenAI** (`gpt-4o-mini`, the default) or **Anthropic** (`claude-sonnet-5-5`).

1. **Exercise generation with tool use.** The backend picks the words that are due for review (spaced repetition) and puts them in the prompt. The AI must answer through a tool schema (`type`, `prompt`, `correct_answer`), so the output is structured JSON, not free text.
2. **Code validates the AI.** `find_exercise_problem` checks every generated exercise: all fields present, exactly one blank, the answer is really the target word, and the answer doesn't already appear in the sentence. A bad exercise is retried up to 3 times. After that the API returns an error instead of showing it.
3. **Graded by code, explained by AI.** Code decides whether an answer is correct ([`backend/answer_check.py`](backend/answer_check.py): normalising, accent hints). The AI only writes the explanation. A model never decides the grade.
4. **Grounding, not RAG.** The facts (words, meanings, review dates) come from the database and are put into the prompt directly.
5. **Saving tokens.** A sentence that hasn't been answered correctly yet is reused from the database instead of calling the AI again.

## Tech stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy, SQLite (a single local file, no server)
- **Frontend:** React + TypeScript (Vite), plain CSS, native `fetch`

## Setup

You need **Python 3.13** and **Node.js 24** (or another recent LTS), plus an **OpenAI API key**.

### 1. Backend (terminal 1)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then open .env and paste your OPENAI_API_KEY
python seed.py                     # creates quicklearner.db and loads the word list
uvicorn main:app --reload
```

The API runs at http://localhost:8000. Interactive API docs (Swagger) are at http://localhost:8000/docs.

### 2. Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Try it

1. **Home** shows your progress. Click **Recommended order**, or pick a topic.
2. **Flashcards:** flip a few cards and press **Got it** on some of them. These words move on to practice.
3. **Practise:** the AI writes a sentence with a blank for one of those words. Type the missing word and press **Check** to see the verdict, the next review date and the AI tutor's explanation. **Skip** and **Next** move on.

## Project structure

```
backend/
  main.py          FastAPI app and all endpoints
  ai_service.py    the only file that calls an AI (chat(), exercise generation, feedback)
  answer_check.py  plain-code answer checking (no AI)
  data_manager.py  database queries
  models.py        SQLAlchemy models (words, exercises, attempts, spaced-repetition cards)
  schemas.py       Pydantic request/response models
  seed.py          builds the database from data/spanish/*.json (safe to rerun)
frontend/src/
  App.tsx          picks the screen
  api.ts           all calls to the backend
  components/      Home, Flashcards, Practise screens and the tab bar
```

## Known limitations

- Single user, local only, no accounts.
- AI-written sentences can occasionally allow more than one sensible answer (e.g. "Hoy es ___ (day)"). The planned fix is a second model acting as a judge.
- Spanish only for now. The schema supports more languages as database rows.
