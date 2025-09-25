import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

user_prompt = "Plan a weekend trip to Washington D.C."

# ----------------------
# Step 1: Intent schema
# ----------------------
intent_schema = {
    "type": "object",
    "properties": {
        "destination": {"type": "string", "minLength": 1},
        "duration": {"type": "string", "minLength": 1}
    },
    "required": ["destination", "duration"],
}

intent_system_prompt = """
You extract minimal intent from a travel request.
Return ONLY JSON with { "destination": string, "duration": string }.
"""


# --------------------------
# Step 2: Activities schema
# --------------------------
activities_schema = {
    "type": "object",
    "properties": {
        "activities": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 3,
            "maxItems": 5
        }
    },
    "required": ["activities"]
}

activities_system_prompt = """
You suggest concise activities for a destination and time window.
Return ONLY JSON with a single key 'activities' mapping to an array of 3-5 short strings. No extra fields or prose.
"""

# -------------------------
# Step 3: Itinerary schema
# -------------------------
itinerary_schema = {
    "type": "object",
    "properties": {},
    "patternProperties": {
        "^Day [1-7]$": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1
        }
    },
}

itinerary_system_prompt = """
You organize a list of activities into a simple day-by-day itinerary.
Return ONLY JSON with keys like "Day 1", "Day 2", each mapping to an array of activities.
"""

def call_with_schema(system_prompt: str, user_prompt: str, schema: dict, name: str):
    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": name,
                "schema": {**schema, "additionalProperties": False},
                "strict": True
            },
        },
    )
    json_text = resp.output_text
    return json.loads(json_text)

# ----------------------
# Run Step 1: Intent
# ----------------------
intent = call_with_schema(intent_system_prompt, user_prompt, intent_schema, "intent")
print("=== Step 1: Intent ===")
print(json.dumps(intent, indent=2))

# ----------------------
# Run Step 2: Activities
# ----------------------
activities_user = (
    f'Given destination "{intent["destination"]}" and duration "{intent["duration"]}", '
    'suggest 3–5 activities suitable for that timeframe. Return only the JSON array.'
)
activities_response_object = call_with_schema(activities_system_prompt, activities_user, activities_schema, "activities")
activities = activities_response_object.get("activities", [])
print("\n=== Step 2: Activities ===")
print(json.dumps(activities, indent=2))

# ----------------------
# Run Step 3: Itinerary
# ----------------------
itinerary_user = (
    "Organize the following activities into a simple day-by-day plan for the given duration. "
    "Return only JSON with keys 'Day 1', 'Day 2', etc.\n\n"
    f"Duration: {intent['duration']}\n"
    f"Activities: {json.dumps(activities)}"
)
itinerary = call_with_schema(itinerary_system_prompt, itinerary_user, itinerary_schema, "itinerary")
print("\n=== Step 3: Itinerary ===")
print(json.dumps(itinerary, indent=2))