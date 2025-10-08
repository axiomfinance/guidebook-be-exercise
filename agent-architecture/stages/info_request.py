import json
from llm_client import client
from tools.mock_db import EVENTS, ATTENDEES, list_attendees

def call_info_request(user_text: str) -> dict:
    """
    Process user queries requesting information about events or attendees.

    Supports multiple query types:
    - List all events
    - Get attendees for specific event(s)
    - Search attendees by name
    - Get attendee counts
    - Find events by attendee email
    """

    # Step 1: Determine the query intent and extract relevant entities
    extraction_schema = {
        "type": "object",
        "properties": {
            "query_type": {
                "type": "string",
                "enum": ["list_events", "get_attendees", "search_attendee", "count_attendees", "find_by_email", "general_info"],
                "description": "Type of information request"
            },
            "events_mentioned": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of event names mentioned (can be empty)"
            },
            "attendee_name": {
                "type": "string",
                "description": "Name of attendee to search for (empty string if not applicable)"
            },
            "attendee_email": {
                "type": "string",
                "description": "Email of attendee to search for (empty string if not applicable)"
            },
            "wants_count": {
                "type": "boolean",
                "description": "Whether user wants counts/statistics"
            }
        },
        "required": ["query_type", "events_mentioned", "attendee_name", "attendee_email", "wants_count"],
        "additionalProperties": False,
    }

    extraction_conversation = [
        {
            "role": "system",
            "content": (
                "Extract the query intent and entities from the user's request. "
                "Determine what type of information they're asking for:\n"
                "- list_events: User wants to see all available events\n"
                "- get_attendees: User wants attendees for specific event(s)\n"
                "- search_attendee: User is looking for a specific person\n"
                "- count_attendees: User wants statistics/counts\n"
                "- find_by_email: User is searching by email\n"
                "- general_info: General information request\n\n"
                "Available events in the system:\n" + "\n".join(f"- {e['name']}" for e in EVENTS)
            ),
        },
        {"role": "user", "content": user_text},
    ]

    extraction_resp = client.responses.create(
        model="gpt-4o-mini",
        input=extraction_conversation,
        text={
            "format": {
                "type": "json_schema",
                "name": "info_request_extraction",
                "schema": extraction_schema,
                "strict": True,
            }
        },
    )

    query_params = json.loads(extraction_resp.output_text)
    query_type = query_params.get("query_type")
    events_mentioned = query_params.get("events_mentioned", [])
    attendee_name = query_params.get("attendee_name", "")
    attendee_email = query_params.get("attendee_email", "")
    wants_count = query_params.get("wants_count", False)

    # Step 2: Execute the appropriate query based on type
    response_data = {"query_type": query_type}

    if query_type == "list_events":
        # Return all events with their details
        response_data["events"] = []
        for event in EVENTS:
            attendees = list_attendees(event["name"])
            response_data["events"].append({
                "id": event["id"],
                "name": event["name"],
                "attendee_count": len(attendees),
                "attendees": attendees if not wants_count else None
            })

    elif query_type == "get_attendees":
        # Get attendees for specific event(s)
        if events_mentioned:
            response_data["events"] = []
            for ev_name in events_mentioned:
                attendees = list_attendees(ev_name)
                response_data["events"].append({
                    "event_name": ev_name,
                    "attendee_count": len(attendees),
                    "attendees": attendees
                })
        else:
            # No specific events, return all
            response_data["events"] = []
            for event in EVENTS:
                attendees = list_attendees(event["name"])
                response_data["events"].append({
                    "event_name": event["name"],
                    "attendee_count": len(attendees),
                    "attendees": attendees
                })

    elif query_type == "search_attendee":
        # Search for attendee by name across all events
        response_data["results"] = []
        search_term = attendee_name.lower() if attendee_name else ""

        for attendee in ATTENDEES:
            if search_term and search_term in attendee["name"].lower():
                # Find which event this attendee is registered for
                event = next((e for e in EVENTS if e["id"] == attendee["event_id"]), None)
                if event:
                    response_data["results"].append({
                        "name": attendee["name"],
                        "email": attendee["email"],
                        "event": event["name"]
                    })

    elif query_type == "count_attendees":
        # Return attendance statistics
        response_data["statistics"] = {
            "total_events": len(EVENTS),
            "total_attendees": len(ATTENDEES),
            "events": []
        }

        for event in EVENTS:
            attendees = list_attendees(event["name"])
            response_data["statistics"]["events"].append({
                "event_name": event["name"],
                "attendee_count": len(attendees)
            })

    elif query_type == "find_by_email":
        # Find events by attendee email
        response_data["results"] = []
        search_email = attendee_email.lower() if attendee_email else ""

        for attendee in ATTENDEES:
            if search_email and search_email in attendee["email"].lower():
                event = next((e for e in EVENTS if e["id"] == attendee["event_id"]), None)
                if event:
                    response_data["results"].append({
                        "name": attendee["name"],
                        "email": attendee["email"],
                        "event": event["name"]
                    })

    else:  # general_info
        # Provide a general overview
        response_data["overview"] = {
            "total_events": len(EVENTS),
            "total_attendees": len(ATTENDEES),
            "events": []
        }

        for event in EVENTS:
            attendees = list_attendees(event["name"])
            response_data["overview"]["events"].append({
                "name": event["name"],
                "id": event["id"],
                "attendee_count": len(attendees)
            })

    return response_data