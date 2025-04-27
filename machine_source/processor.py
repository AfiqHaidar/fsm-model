import csv
import json
import os
from datetime import datetime

# ==== CONSTANTS ====
DELIMITER = ","


def extract_states_and_transitions(input_csv, extract_function):
    """Extract states, transitions, and triggers using the provided extraction function."""
    states = []
    transitions = set()
    previous_state = None

    with open(input_csv, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=DELIMITER)

        for row in reader:

            extracted_data = extract_function(row)
            if not extracted_data:
                continue

            state, trigger = extracted_data  # Extract state & trigger
            if state not in states:
                states.append(state)

            if previous_state and previous_state != state:
                transitions.add((previous_state, state, trigger))

            previous_state = state

    return states, sorted(transitions)


def generate_json(input_csv, output_dir, extract_function, prefix):
    """
    Generate a JSON file using the given extraction function.

    :param input_csv: Path to the CSV file.
    :param output_dir: Directory to save the JSON.
    :param extract_function: Function to extract states and triggers.
    :param prefix: Prefix for the JSON filename.
    """
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create subdirectory based on extractor type (e.g., domain, url)
    output_subdir = os.path.join(output_dir, prefix)
    os.makedirs(output_subdir, exist_ok=True)

    output_json = os.path.join(output_subdir, f"{prefix}_{current_time}.json")

    states, transitions = extract_states_and_transitions(
        input_csv, extract_function)

    # Extract unique triggers from transitions
    unique_triggers = {trigger for _, _, trigger in transitions}

    json_data = {
        "WebActivityMachine": [
            {
                "name": f"{prefix}_{current_time}",
                "initial_state": states[0] if states else "unknown",
                "states": states,
                # Include all unique triggers
                "triggers": list(unique_triggers),
                "transitions": [{"trigger": trigger, "source": src, "dest": dst} for src, dst, trigger in transitions],
                "functions": {}
            }
        ]
    }

    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON saved to {output_json}")
