import json
from llm_client import client

def call_validate_input(user_text: str) -> dict:
    """
    Validate user input specifically for the events domain.

    Returns:
        dict with keys:
            - valid (bool): True if input is relevant/parseable
            - reason (str): Short explanation if invalid
    """
    schema = {
        "type": "object",
        "properties": {
            "valid": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["valid", "reason"],
        "additionalProperties": False,
    }

    conversation = [
        {
            "role": "system",
            "content": (
                "You are a domain-specific validator for an events management system. "
                "Your job is to validate whether the user's input is relevant to event management in any way. "
                "Instructions:\n"
                "- Return valid=True if the input is relevant to event management in any way.\n"
                "- Return valid=False if the input is irrelevant, ambiguous, or cannot be mapped to the domain.\n"
            ),
        },
        {"role": "user", "content": user_text},
    ]

    response = client.responses.create(
        model="gpt-4o",
        input=conversation,
        text={
            "format": {
                "type": "json_schema",
                "name": "validation_response",
                "schema": schema,
                "strict": True,
            }
        },
    )

    parsed = json.loads(response.output_text)

    return parsed
