import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = "Explain what AI is in one sentence."

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
)

print("=== Full Response ===")
# print(response.output_text)
print(json.dumps(response.model_dump(), indent=2))