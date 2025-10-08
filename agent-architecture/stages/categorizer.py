import json
from llm_client import client

def call_categorize(user_text: str, events_context: str) -> dict:
    schema = {
        "type": "object",
        "properties": {
            "category": {"type": "string", "description": "One of: registration, info_request, other"},
            "confidence": {"type": "number"},
        },
        "required": ["category", "confidence"],
        "additionalProperties": False,
    }

    conversation = [
        {
            "role": "system",
            "content": f"Classify user requests into registration, info_request, or other. Events:\n{events_context}. Use confidence to indicate how confident you are in your classification. Confidence should be a number between 0 and 1. 1 is the highest confidence."
        },
        {"role": "user", "content": user_text},
    ]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=conversation,
        text={
            "format": {
                "type": "json_schema",
                "name": "categorization_response",
                "schema": schema,
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)
