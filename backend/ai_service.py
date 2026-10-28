# backend/ai_service.py
# Everything that talks to OpenAI lives here.
# Each function follows the same 5 steps: input -> config -> messages -> API call -> parse.
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads OPENAI_API_KEY from backend/.env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_TRIES = 3  # how many times to ask the AI again if it breaks a rule


def generate_exercise_from_words(domain_name: str, system_prompt: str, vocabulary_items: list):
    """
    Asks the AI to write one fill-in-the-blank exercise.
    vocabulary_items: list of VocabularyItem objects (already fetched from the db).
    The FIRST item is the target word (the answer); the rest are optional extra words.
    Returns a dict like {"type": ..., "prompt": ..., "correct_answer": ...}
    """

    # 1. Input: one target word (the answer), the rest are optional extras
    target = vocabulary_items[0]
    other_words = ", ".join(item.term for item in vocabulary_items[1:]) or "none"
    level = target.cefr_level or "A1"

    # 2. Configuration
    model_name = "gpt-4o-mini"
    temperature = 0.7  # a bit creative, so exercises vary

    # 3. Messages
    # (in an f-string, {{ and }} mean a literal { and } in the text)
    user_prompt = f"""Write ONE fill-in-the-blank exercise in {domain_name} for a learner at CEFR level {level}.

                    Target word (this is the answer): {target.term} (meaning: {target.definition})
                    Optional extra words you may use in the sentence: {other_words}

                    Rules:
                    - Write ONE short, natural sentence suitable for level {level}.
                    - The sentence has exactly ONE blank, written as ___, where the target word goes.
                    - The target word must NOT appear anywhere else in the sentence.
                    - The blank must take the target word in exactly this form: "{target.term}" (do not conjugate it or make it plural).
                    - Put the English meaning in brackets right after the blank, like: ___ ({target.definition})

                    Return ONLY valid JSON, no other text, in exactly this shape:
                    {{
                    "type": "fill_blank",
                    "prompt": "the sentence shown to the learner, with the blank marked as ___",
                    "correct_answer": "{target.term}"
                    }}"""

    messages = [
        # comes from the Domain row in the db
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 4 + 5. API call and parse, asking again if the AI breaks a rule
    for try_number in range(1, MAX_TRIES + 1):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},  # forces a valid JSON reply
        )

        raw_content = response.choices[0].message.content
        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            print(f"Try {try_number}: not valid JSON: {raw_content}")
            continue  # skip to the next try

        problem = find_exercise_problem(data, target.term)
        if problem is None:
            return data  # passed every check
        print(f"Try {try_number}: rejected ({problem}): {data}")

    raise ValueError(
        f"AI could not write a valid exercise after {MAX_TRIES} tries")


def find_exercise_problem(data: dict, target_term: str):
    """
    Checks the AI's exercise against our rules, in code (we don't just trust the AI).
    Returns a short description of the first problem found, or None if it's fine.
    """
    if "type" not in data or "prompt" not in data or "correct_answer" not in data:
        return "missing fields"

    prompt = data["prompt"].lower()
    answer = data["correct_answer"].strip().lower()
    target = target_term.lower()

    if prompt.count("___") != 1:
        return "needs exactly one blank"
    if answer != target:
        return "answer is not the target word"
    if target in prompt:
        return "answer appears in the sentence"

    return None


def evaluate_answer(system_prompt: str, exercise_prompt: str, correct_answer: str,
                    user_answer: str, is_correct: bool):
    """
    Asks the AI to explain an answer that main.py has already graded.
    is_correct: True or False, from main.py's exact-match check.
    Returns the feedback text (a string).
    """

    # 1. Input: pick the grading instruction
    if is_correct:
        verdict_instruction = "The answer has already been graded as CORRECT. Explain why."
    else:
        verdict_instruction = "The answer has already been graded as INCORRECT. Explain why."

    # 2. Configuration
    model_name = "gpt-4o-mini"
    temperature = 0.3  # low, so grading is consistent

    # 3. Messages
    user_prompt = f"""A learner answered this exercise.

                    Exercise: {exercise_prompt}
                    Expected answer: {correct_answer}
                    Learner's answer: {user_answer}

                    {verdict_instruction}

                    Write feedback in 1-3 short sentences, in English, addressed to the learner. If the answer is wrong, explain the mistake (spelling, accents, gender, conjugation, wrong word, etc.) without being discouraging. If it's right, confirm it and add one short useful tip.

                    Return ONLY valid JSON in exactly this shape:
                    {{
                    "feedback": "your feedback here"
                    }}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 4. API call
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    # 5. Parse
    raw_content = response.choices[0].message.content
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise ValueError(f"AI response was not valid JSON: {raw_content}")

    if "feedback" not in data:
        raise ValueError(f"AI response is missing fields: {data}")

    return data["feedback"]
