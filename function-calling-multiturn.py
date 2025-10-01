import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------
# Mock relational "tables"
# ------------------------
EVENTS = [
    {"id": 1, "name": "Developer Meetup"},
    {"id": 2, "name": "AI Conference"},
]

ATTENDEES = [
    {"id": 1, "event_id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "event_id": 1, "name": "Jane Smith", "email": "jane@example.com"},
    {"id": 3, "event_id": 2, "name": "Alice Johnson", "email": "alice@example.com"},
]

# ------------------------
# Mock relational functions
# ------------------------
def list_attendees(event_id: int) -> list[dict]:
    '''Get all attendees registered for a specific event.'''
    attendees = []
    for attendee in ATTENDEES:
        if attendee['event_id'] == event_id:
            attendees.append(attendee)
    return attendees

def add_attendee(event_id: int, name: str, email: str) -> dict:
    '''Register a new attendee for an event.'''
    existing_ids = [attendee['id'] for attendee in ATTENDEES]
    new_id = max(existing_ids) + 1
    
    new_attendee = {
        'id': new_id,
        'event_id': event_id,
        'name': name,
        'email': email
    }
    
    ATTENDEES.append(new_attendee)
    return {
        'success': True,
        'attendee': new_attendee,
        'all_attendees': ATTENDEES
    }

def get_events() -> str:
    '''Return a formatted string listing all events with their IDs.'''
    event_lines = []
    for event in EVENTS:
        event_line = f'{event["id"]}: {event["name"]}'
        event_lines.append(event_line)
    return '\n'.join(event_lines)

# ------------------------
# Function schemas for AI
# ------------------------
tools = [
    {
        "type": "function",
        "name": "list_attendees",
        "description": "List all attendees for a given event",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "integer", "description": "The ID of the event"},
            },
            "required": ["event_id"],
        },
    },
    {
        "type": "function",
        "name": "add_attendee",
        "description": "Add a new attendee to an event",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["event_id", "name", "email"],
        },
    },
]

# ------------------------
# System message
# ------------------------
system_message = {
    "role": "system",
    "content": (
        "You are an assistant that helps manage events and attendees.\n"
        f"Here are the available events with their IDs:\n{get_events()}\n"
        "Always use the correct event_id when calling tools."
    ),
}

# ------------------------
# Conversation state
# ------------------------
conversation = [system_message]

# ------------------------
# Terminal I/O loop
# ------------------------
print("Interactive Event Assistant (type 'exit' to quit)\n")
while True:
    user_input = input("User: ")
    if user_input.strip().lower() == "exit":
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.responses.create(
        model="gpt-4.1",
        input=conversation,
        tools=tools,
    )

    # Print assistant text
    print(f"\nAssistant: {response.output_text}")

    # Handle any function calls
    for item in response.output:
        if item.type == 'function_call':
            args = json.loads(item.arguments)
            if item.name == 'list_attendees':
                result = list_attendees(args['event_id'])
                print(f"\n[Tool Call] {item.name}({args}) -> {json.dumps(result, indent=2)}")
                print(f"Here are the attendees for the event:\n {json.dumps(result, indent=2)}")
            elif item.name == 'add_attendee':
                result = add_attendee(args['event_id'], args['name'], args['email'])
                print(f"\n[Tool Call] {item.name}({args}) -> {json.dumps(result, indent=2)}")
                print("That user is registered for the event!")

            else:
                result = {"error": "Unknown tool"}

            # Print tool result

            # Append tool result as assistant message
            conversation.append({
                "role": "assistant",
                "content": f"[Tool Result] {json.dumps(result)}"
            })
        elif item.type == 'output_text':
                print(f"\nAssistant: {item.content}")

    print("\n---")  