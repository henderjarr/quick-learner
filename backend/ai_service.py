# backend/ai_service.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_exercise_from_words(domain_name: str, system_prompt: str, vocabulary_items: list):
    """
    vocabulary_items: list of VocabularyItem objects (already fetched from the db)
    Returns a dict matching what we'll save into the Exercise table.
    """

    # Build a simple text list of the words to give the AI as context
    word_list = "\n".join(
        f"- {item.term} ({item.definition})" for item in vocabulary_items)

    user_prompt = f"""Generate ONE short practice exercise in {domain_name} that uses ALL of the following words together naturally, ideally in a single sentence or short exchange: {word_list} Return ONLY valid JSON, no other text, in exactly this shape:
                    {{
                    "type": "fill_blank",
                    "prompt": "the exercise text shown to the learner, with a blank marked as ___",
                    "correct_answer": "the correct word or phrase that fills the blank"
                    }}

                   """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    raw_text = response.choices[0].message.content

    try:
        exercise_data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"AI response was not valid JSON: {raw_text}")

    return exercise_data


def evaluate_answer(system_prompt: str, exercise_prompt: str, correct_answer: str,
                    user_answer: str, known_is_correct: bool = None):
    """
    Asks the AI to judge a learner's answer and explain it.
    known_is_correct: if the caller already decided correctness (e.g. exact match
    for fill_blank), pass it in so the AI explains that verdict instead of judging.
    Returns a dict: {"is_correct": bool, "feedback": str}
    """

    if known_is_correct is None:
        verdict_instruction = (
            "Decide whether the learner's answer is correct. Accept answers that are "
            "grammatically correct and mean the same thing as the expected answer, "
            "even if worded differently."
        )
    else:
        verdict = "CORRECT" if known_is_correct else "INCORRECT"
        verdict_instruction = (
            f"The answer has already been graded as {verdict}. Set is_correct to "
            f"{str(known_is_correct).lower()} and explain why."
        )

    user_prompt = f"""A learner answered this exercise.

Exercise: {exercise_prompt}
Expected answer: {correct_answer}
Learner's answer: {user_answer}

{verdict_instruction}

Write feedback in 1-3 short sentences, in English, addressed to the learner. If the answer is wrong, explain the mistake (spelling, accents, gender, conjugation, wrong word, etc.) without being discouraging. If it's right, confirm it and add one short useful tip.

Return ONLY valid JSON in exactly this shape:
{{
"is_correct": true or false,
"feedback": "your feedback here"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        # forces the model to return valid JSON
        response_format={"type": "json_object"}
    )

    raw_text = response.choices[0].message.content

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"AI response was not valid JSON: {raw_text}")

    if not isinstance(result.get("is_correct"), bool) or "feedback" not in result:
        raise ValueError(f"AI response had the wrong shape: {raw_text}")

    return result
