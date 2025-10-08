EVENTS = [
    {"id": 1, "name": "Developer Meetup"},
    {"id": 2, "name": "AI Conference"},
]

ATTENDEES = [
    {"id": 1, "event_id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "event_id": 2, "name": "Jane Smith", "email": "jane@example.com"},
]

def get_events_context():
    return "\n".join(f"{e['id']}: {e['name']}" for e in EVENTS)

def list_attendees(event_name):
    event = next((e for e in EVENTS if e["name"].lower() == event_name.lower()), None)
    if not event:
        return []
    return [a for a in ATTENDEES if a["event_id"] == event["id"]]

def add_attendee(event_name, name, email):
    event = next((e for e in EVENTS if e["name"].lower() == event_name.lower()), None)
    if not event:
        return {"error": "Event not found"}
    new_id = max(a["id"] for a in ATTENDEES) + 1
    new_attendee = {"id": new_id, "event_id": event["id"], "name": name, "email": email}
    ATTENDEES.append(new_attendee)
    return new_attendee
