import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation = [
  {"role": "system", "content": "You are a concise technical assistant."},
  {"role": "user", "content": "Explain what AI is in one sentence."},
  {"role": "assistant", "content": "AI, or artificial intelligence, refers to the capability of a machine to simulate human intelligence processes such as learning, reasoning, problem-solving, and understanding natural language."}, # Add response from previous prompt
  {"role": "user", "content": "Can you give me some of the larger companies in the AI space?"}, # Add follow-up question
]

response = client.responses.create(
  model="gpt-4o-mini",
  input=conversation,
)

print("=== Assistant Reply ===")
print(response.output_text)

# print("\n=== Full Response ===")
# print(json.dumps(response.model_dump(), indent=2))