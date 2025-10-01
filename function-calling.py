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
# Conversation
# ------------------------
system_message = {
    "role": "system",
    "content": (
        "You are an assistant that helps manage events and attendees.\n"
        "Here are the available events with their IDs:\n"
        f"{get_events()}\n"
        "Always use the correct event_id when calling tools."
    ),
}

conversation_1 = [
    system_message,
    {"role": "user", "content": "Who is attending the AI Conference?"},
    # {"role": "user", "content": "Who is attending the Developer Meetup?"},
]

conversation_2 = [
    system_message,
    {"role": "user", "content": "Add a new attendee to the Developer Meetup: Shyam K, shyam@example.com"},
]

conversation_3 = [
    system_message,
    {"role": "user", "content": "Who is attending the AI Conference? Also add a new attendee to the event: Shyam K, shyam@example.com"},
]

response = client.responses.create(
    model="gpt-4.1",
    input=conversation_1,
    tools=tools,
)

print("=== Assistant Reply ===")
print(json.dumps(response.model_dump(), indent=2))

# ------------------------
# Tool calls (pretty print + mock execution)
# ------------------------
print("\n=== Tool Calls ===")
for item in response.output:
    if item.type == 'function_call':
        args = json.loads(item.arguments)
        print(f"- {item.name}: {args}")
        
        if item.name == 'list_attendees':
            result = list_attendees(args['event_id'])
            print(f"  -> result: {json.dumps(result, indent=2)}")
        elif item.name == 'add_attendee':
            result = add_attendee(args['event_id'], args['name'], args['email'])
            print(f"  -> result: {json.dumps(result, indent=2)}")
    elif item.type == 'output_text':
        print(f"  -> result: {item.content}")