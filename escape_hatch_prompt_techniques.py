import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# JSON SCHEMA (Validation)
# =========================

escape_hatch_schema = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "answer": {"type": "string"},
    },
    "required": ["reasoning", "answer"],
}

# ======================================
# SYSTEM PROMPT
# ======================================

escape_hatch_system_prompt = """
You are a concise technical assistant.

Use these techniques:
1) REASONING: Provide a short, high-level "reasoning" for your answer.
2) ESCAPE HATCH: If the question requires up-to-date facts, proprietary data, or unverifiable speculation, set "answer":"cannot_answer".

Formatting rules:
- Return ONLY JSON that validates against the schema. No markdown, no text outside JSON.
- Keep answers concise and useful. If list is expected, return an array of strings in "answer".
"""

# ======================================
# USER PROMPTS
# ======================================
PROMPTS = {
    # Likely high confidence; returns a comma separated list. Demonstrates structured "answer" + high confidence.
    "no_escape_hatch_answer": "Return the names of five large, public AI companies. Output only the names in a comma separated list.",

    # Another escape hatch example (speculative prediction); should set answer='cannot_answer'.
    "escape_hatch_answer": "What will Apple's stock price be on December 31, 2026? Provide a number."
}


# Choose ONE to run:
USER_PROMPT = PROMPTS["no_escape_hatch_answer"]
# USER_PROMPT = PROMPTS["escape_hatch_answer"]


response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": escape_hatch_system_prompt.strip()},
        {"role": "user", "content": USER_PROMPT}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "answer_response",
            "schema": {**escape_hatch_schema, "additionalProperties": False},
            "strict": True
        }
    },
)

print("=== Response ===")
json_text = response.output_text
parsed = json.loads(json_text)
print(json.dumps(parsed, indent=2))
