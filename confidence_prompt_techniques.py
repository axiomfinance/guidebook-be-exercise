import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# JSON SCHEMA (Validation)
# =========================
# Enforces structured outputs + supports confidence & escape hatch logic.
confidence_schema = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "answer": {"type": "string"},
    },
    "required": ["reasoning", "confidence", "answer"],
}

# ======================================
# SYSTEM PROMPT
# ======================================
confidence_system_prompt = """
You are a concise technical assistant.

Use these techniques:
1) REASONING: Provide a short, high-level "reasoning" for your answer.
2) CONFIDENCE: Always include an integer "confidence" from 1-5 reflecting certainty in your result. 5 is the highest confidence.

Formatting rules:
- Return ONLY JSON that validates against the schema. No markdown, no text outside JSON.
- Keep answers concise and useful. If list is expected, return an array of strings in "answer".
"""


# ======================================
# USER PROMPTS
# ======================================
PROMPTS = {
    # Likely high confidence; returns a comma separated list. Demonstrates structured "answer" + high confidence.
    "high_confidence_answer": "Return the names of five large, public AI companies. Output only the names in a comma separated list.",

    # Another escape hatch example (speculative prediction); should set answer='cannot_answer'.
    "low_confidence_answer": "What will Apple's stock price be on December 31, 2026? Provide a number."
}
# Choose ONE to run:
USER_PROMPT = PROMPTS["high_confidence_answer"]
# USER_PROMPT = PROMPTS["low_confidence_answer"]

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": confidence_system_prompt.strip()},
        {"role": "user", "content": USER_PROMPT}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "answer_response",
            "schema": {**confidence_schema, "additionalProperties": False},
            "strict": True
        }
    },
)

print("=== Response ===")
json_text = response.output_text
parsed = json.loads(json_text)
print(json.dumps(parsed, indent=2))
