from tools.mock_db import get_events_context, add_attendee
from stages.input_validator import call_validate_input
from stages.categorizer import call_categorize
from stages.registration import call_extract_registration
from stages.info_request import call_info_request
from stages.output import call_compose_output

def main():
    user_text = input("User: ")

    # Step 1: Validate input is relevant to event management domain
    validation = call_validate_input(user_text)
    if not validation["valid"]:
        print("→ Sorry, I don't understand that. Please try again.")
        return

    # Step 2: Categorize request type (registration, info_request, other)
    category = call_categorize(user_text, get_events_context())
    if category.get("confidence", 0) <= 0.8:
        print("→ I'm not quite sure what you're asking. Could you please rephrase your request?")
        return

    # Step 3: Route to appropriate handler based on category
    result = None
    if category["category"] == "registration":
        data = call_extract_registration(user_text, get_events_context())
        result = add_attendee(data["event_name"], data["name"], data["email"])
    elif category["category"] == "info_request":
        result = call_info_request(user_text)
    else:
        result = {"message": "No matching route."}

    # Step 4: Compose user-friendly response
    final_message = call_compose_output(result, category["category"])
    print("\nAssistant:", final_message)


if __name__ == "__main__":
    main()
