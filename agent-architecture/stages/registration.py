import json
from llm_client import client

def call_extract_registration(user_text: str, events_context: str) -> dict:
    schema = {
        "type": "object",
        "properties": {
            "event_name": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
        "required": ["event_name", "name", "email"],
        "additionalProperties": False,
    }

    conversation = [
        {"role": "system", "content": f"Extract event_name, name, and email from this text. Events:\n{events_context}"},
        {"role": "user", "content": user_text},
    ]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=conversation,
        text={
            "format": {
                "type": "json_schema",
                "name": "registration_extraction",
                "schema": schema,
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)
