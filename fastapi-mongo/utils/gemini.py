import requests
import json
import re
from quizzly.core.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY


def generate_questions(subject: str, topic: str, num_questions: int, difficulty_level: int):
    PROMPT_TEMPLATE = f"""
    You are a teaching assistant tasked with creating {num_questions} Multiple choice questions on the subject {subject} and topic {topic} with 4 choices (A,B,C,D) in the format:\n
    "questions": [
        {{
            "question": "What is the output of print(type([]))?",
            "choice_A": "<class 'list'>",
            "choice_B": "<class 'dict'>",
            "choice_C": "<class 'tuple'>",
            "choice_D": "<class 'set'>",
            "answer": "A",
            "is_correct": false
        }},
        {{
            "question": "Which keyword is used to create a function in Python?",
            "choice_A": "func",
            "choice_B": "def",
            "choice_C": "function",
            "choice_D": "lambda",
            "answer": "B",
            "is_correct": false
        }}
    ]
    Keep the difficulty according to {difficulty_level} level, where level 1 -> class 1 student should answer them and level -> 10 should be class 10 student should answer them.
    I want {num_questions} generated questions on the topic {topic} only and they should strictly be in the format as shown in the example above (as a list of dictionaries). The default value of is_correct should be false. Only include the questions in your answer, nothing else.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": PROMPT_TEMPLATE
                    }
                ]
            }
        ]
    }

    # Headers to define content type and API key
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
    except Exception as e:
        raise e

    if response.status_code == 200:
        resp = extract_questions_from_gemini_response(response.content)
        return resp


def extract_questions_from_gemini_response(response_content: bytes):
    response_str = response_content.decode('utf-8')
    response_json = json.loads(response_str)
    model_text = response_json['candidates'][0]['content']['parts'][0]['text']
    model_text = re.sub(r'^```json|```$', '', model_text.strip(), flags=re.MULTILINE).strip("`")
    parsed_output = json.loads(model_text)
    return parsed_output.get("questions", [])
