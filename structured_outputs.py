import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a schema where the assistant must return a JSON object with a field "companies" that is a list of strings.
# Docs: https://json-schema.org/docs/
# Can also use zod or pydantic to define the schema
schema = {
    "type": "object",
    "properties": {
        "companies": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["companies"],
}

conversation = [
    {"role": "system", "content": "You are a concise technical assistant."},
    {"role": "user", "content": "Explain what AI is in one sentence."},
    {"role": "assistant", "content": "AI, or artificial intelligence, refers to the capability of a machine to simulate human intelligence processes such as learning, reasoning, problem-solving, and understanding natural language."},
    {"role": "user", "content": "Can you give me some of the larger companies in the AI space?"},
]

response = client.responses.create(
    model="gpt-4o-mini",
    input=conversation,
    text={
        "format": {
            "type": "json_schema",
            "name": "companies_response",
            "schema": {
                **schema,
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

print("=== Raw Response ===")
print(json.dumps(response.model_dump(), indent=2))

# print("\n=== Parsed JSON ===")
# # Parse the JSON from the response output
# json_text = response.output[0].content[0].text
# parsed_json = json.loads(json_text)
# print(json.dumps(parsed_json, indent=2))