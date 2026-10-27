# backend/ai_service.py
# Everything that talks to OpenAI lives here.
# Each function follows the same 5 steps: input -> config -> messages -> API call -> parse.
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads OPENAI_API_KEY from backend/.env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_exercise_from_words(domain_name: str, system_prompt: str, vocabulary_items: list):
    """
    Asks the AI to write one exercise using the given words.
    vocabulary_items: list of VocabularyItem objects (already fetched from the db)
    Returns a dict like {"type": ..., "prompt": ..., "correct_answer": ...}
    """

    # 1. Input: turn the words into a simple text list
    word_list = "\n".join(
        f"- {item.term} ({item.definition})" for item in vocabulary_items)

    # 2. Configuration
    model_name = "gpt-4o-mini"
    temperature = 0.7  # a bit creative, so exercises vary

    # 3. Messages
    # (in an f-string, {{ and }} mean a literal { and } in the text)
    user_prompt = f"""Generate ONE short practice exercise in {domain_name} that uses ALL of the following words together naturally, ideally in a single sentence or short exchange:
                    {word_list}

                    Return ONLY valid JSON, no other text, in exactly this shape:
                    {{
                    "type": "fill_blank",
                    "prompt": "the exercise text shown to the learner, with a blank marked as ___",
                    "correct_answer": "the correct word or phrase that fills the blank"
                    }}"""

    messages = [
        # comes from the Domain row in the db
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 4. API call
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},  # forces a valid JSON reply
    )

    # 5. Parse: JSON string -> Python dict, then check the fields we need are there
    raw_content = response.choices[0].message.content
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise ValueError(f"AI response was not valid JSON: {raw_content}")

    if "type" not in data or "prompt" not in data or "correct_answer" not in data:
        raise ValueError(f"AI response is missing fields: {data}")

    return data


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
