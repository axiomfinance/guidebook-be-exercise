import json
from llm_client import client

def call_compose_output(intermediate_result: dict, category: str) -> str:
    conversation = [
        {"role": "system", "content": f"Compose a clear user-facing message for category '{category}'."},
        {"role": "user", "content": json.dumps(intermediate_result)},
    ]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=conversation,
    )
    return response.output_text
