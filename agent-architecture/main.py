from tools.mock_db import get_events_context, add_attendee
from stages.input_validator import call_validate_input
from stages.categorizer import call_categorize
from stages.registration import call_extract_registration
from stages.info_request import call_info_request
from stages.output import call_compose_output

def main():
    print("\n" + "="*60)
    print("PROMPT CHAINING DEMO - Event Management System")
    print("="*60)

    user_text = input("\nUser: ")
    print("\n" + "-"*60)

    # Step 1: Validate
    print("\n[STEP 1: INPUT VALIDATION]")
    print(f"Input: '{user_text}'")
    print("→ Checking if input is relevant to event management...")
    validation = call_validate_input(user_text)
    print(f"Output: {validation}")

    if not validation["valid"]:
        print("\n❌ VALIDATION FAILED")
        print("→ Sorry, I don't understand that. Please try again.")
        return

    print("✓ Validation passed")
    print("-"*60)

    # Step 2: Categorize
    print("\n[STEP 2: CATEGORIZATION]")
    print(f"Input: '{user_text}'")
    print(f"Context: {get_events_context()}")
    print("→ Determining request type (registration, info_request, feedback, other)...")
    category = call_categorize(user_text, get_events_context())
    print(f"Output: {category}")

    # Check confidence level
    if category.get("confidence", 0) <= 0.8:
        print(f"\n⚠️ LOW CONFIDENCE ({category.get('confidence', 0)})")
        print("→ I'm not quite sure what you're asking. Could you please rephrase your request?")
        return

    print(f"✓ Category: {category['category']} (confidence: {category.get('confidence', 0)})")
    print("-"*60)

    # Step 3: Route
    print(f"\n[STEP 3: ROUTING TO '{category['category'].upper()}' HANDLER]")
    result = None
    if category["category"] == "registration":
        print(f"Input: '{user_text}'")
        print(f"Available events: {get_events_context()}")
        print("→ Extracting registration details (event, name, email)...")
        data = call_extract_registration(user_text, get_events_context())
        print(f"Extracted data: {data}")
        print("→ Adding attendee to database...")
        result = add_attendee(data["event_name"], data["name"], data["email"])
        print(f"Database result: {result}")
    elif category["category"] == "info_request":
        print(f"Input: '{user_text}'")
        print("→ Processing information request...")
        result = call_info_request(user_text)
        print(f"Query result: {result}")
    else:
        result = {"message": "No matching route."}
        print(f"No handler found for category: {category['category']}")

    print("-"*60)

    # Step 4: Compose final output
    print("\n[STEP 4: OUTPUT COMPOSITION]")
    print(f"Input data: {result}")
    print(f"Category: {category['category']}")
    print("→ Generating user-friendly response...")
    final_message = call_compose_output(result, category["category"])
    print(f"\n{'='*60}")
    print("FINAL OUTPUT:")
    print(f"{'='*60}")
    print(f"\nAssistant: {final_message}")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
