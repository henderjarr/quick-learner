# backend/ai_service.py
# Everything that talks to OpenAI lives here.
# Each function follows the same 5 steps: input -> config -> messages -> API call -> parse.
import os
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from answer_check import normalize_answer, remove_brackets, contains_whole_word

load_dotenv()  # reads OPENAI_API_KEY from backend/.env

openAi_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic()
model = "claude-sonnet-5-5"

MAX_TRIES = 3  # how many times to ask the AI again if it breaks a rule

# Helper functions --------------------------------------


# AI helpers
def chat(messages, system=None, tool=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }
    if system:
        params["system"] = system
    if tool:
        params["tools"] = [tool]

    response = anthropic_client.messages.create(**params)

    text = "".join(block.text for block in response.content if block.type == "text")
    tool_input = next(
        (block.input for block in response.content if block.type == "tool_use"), None
    )
    return text, tool_input


# Check helpers
def find_exercise_problem(data: dict, target):
    """
    Checks the AI's exercise against our rules, in code (we don't just trust the AI).
    target: the VocabularyItem the exercise is for.
    Returns a short description of the first problem found, or None if it's fine.
    """
    if "type" not in data or "prompt" not in data or "correct_answer" not in data:
        return "missing fields"

    prompt = str(data["prompt"])
    # compare the same way grading does, so "¿cuánto cuesta?" matches "cuánto cuesta"
    answer = normalize_answer(str(data["correct_answer"]))
    term = normalize_answer(target.term)

    if prompt.count("___") != 1:
        return "needs exactly one blank"
    if answer != term:
        return "answer is not the target word"

    # Leak check. First remove the English hint in brackets, because for cognates
    # like "hotel" the hint is the answer, and that's expected.
    sentence = prompt.replace(target.definition, "")
    # regex backup check to make sure the ai didnt add any brackets etc
    sentence = remove_brackets(sentence)
    # Then look for the answer as a WHOLE word, so "de" doesn't match inside "desayuno".
    # (?<!\w) and (?!\w) mean "no letter right before / right after".
    if contains_whole_word(sentence, term):
        return "answer appears in the sentence"

    return None


# -----------------------------------------------------------


# Tool schemas ----------------------------------------
exercise_tool = {
    "name": "save_exercise",
    "description": "Save one fill-in-the-blank exercise for the learner.",
    "input_schema": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "description": "Always 'fill_blank'."},
            "prompt": {
                "type": "string",
                "description": "The sentence with exactly one ___ blank.",
            },
            "correct_answer": {
                "type": "string",
                "description": "The word that goes in the blank.",
            },
        },
        "required": ["type", "prompt", "correct_answer"],
    },
}

# -----------------------------------------------------------


# AI functions ----------------------------------------------
def generate_exercise_from_words(domain_name, system_prompt, vocabulary_items):
    target = vocabulary_items[0]
    other_words = ", ".join(item.term for item in vocabulary_items[1:]) or "none"
    level = target.cefr_level or "A1"

    user_prompt = f"""Write ONE fill-in-the-blank exercise in {domain_name} for a learner at CEFR level {level}.

                    Target word (this is the answer): {target.term} (meaning: {target.definition})
                    Optional extra words you may use: {other_words}

                    Rules:
                    - ONE short, natural sentence suitable for level {level}.
                    - Exactly ONE blank, written as ___, where the target word goes.
                    - The target word must NOT appear anywhere else in the sentence.
                    - Use the target word in exactly this form: "{target.term}".
                    - Put the English meaning in brackets right after the blank, like: ___ ({target.definition})

                    Use the save_exercise tool to save it."""

    messages = [{"role": "user", "content": user_prompt}]

    for try_number in range(1, MAX_TRIES + 1):
        _, tool_input = chat(messages, system=system_prompt, tool=exercise_tool)

        if tool_input is None:
            print(f"Try {try_number}: Claude didn't use the tool")
            continue

        problem = find_exercise_problem(tool_input, target)
        if problem is None:
            return tool_input
        print(f"Try {try_number}: rejected ({problem}): {tool_input}")

    raise ValueError(f"AI could not write a valid exercise after {MAX_TRIES} tries")


def evaluate_answer(
    system_prompt, exercise_prompt, correct_answer, user_answer, is_correct
):
    if is_correct:
        verdict = "The answer has already been graded as CORRECT. Explain why."
    else:
        verdict = "The answer has already been graded as INCORRECT. Explain why."

    user_prompt = f"""A learner answered this exercise.

                    Exercise: {exercise_prompt}
                    Expected answer: {correct_answer}
                    Learner's answer: {user_answer}

                    {verdict}

                    Write feedback in 1-3 short sentences, in English, addressed to the learner.
                    If the answer is wrong, explain the mistake without being discouraging.
                    If it's right, confirm it and add one short useful tip.
                    Reply with only the feedback text, nothing else."""

    messages = [{"role": "user", "content": user_prompt}]
    text, _ = chat(messages, system=system_prompt)
    return text


# -----------------------------------------------------------
