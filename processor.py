import csv
import json
import os
from datetime import datetime

# ==== CONSTANTS ====
DELIMITER = ","
FILTER_SOURCE = "WEBHIST"


def extract_states_and_transitions(input_csv, extract_function):
    """Extract states and transitions using the provided extraction function."""
    states = []
    transitions = set()
    previous_state = None

    with open(input_csv, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=DELIMITER)

        for row in reader:
            if row.get("source") != FILTER_SOURCE:
                continue

            message = row.get("message", "")
            if not message:
                continue

            # Use the provided extractor function
            state = extract_function(message)
            if not state:
                continue

            if state not in states:
                states.append(state)

            if previous_state and previous_state != state:
                transitions.add((previous_state, state))

            previous_state = state

    return states, sorted(transitions)


def generate_json(input_csv, output_dir, extract_function, prefix):
    """
    Generate a JSON file using the given extraction function.

    :param input_csv: Path to the CSV file.
    :param output_dir: Directory to save the JSON.
    :param extract_function: Function to extract states.
    :param prefix: Prefix for the JSON filename.
    """
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create subdirectory based on the extractor type (e.g., domain, url)
    output_subdir = os.path.join(output_dir, prefix)
    os.makedirs(output_subdir, exist_ok=True)

    output_json = os.path.join(output_subdir, f"{prefix}_{current_time}.json")

    states, transitions = extract_states_and_transitions(
        input_csv, extract_function)

    json_data = {
        "WebActivityMachine": [
            {
                "name": f"{prefix.capitalize()}_{current_time}",
                "initial_state": states[0] if states else "unknown",
                "states": states,
                "triggers": ["next"],
                "transitions": [{"trigger": "next", "source": src, "dest": dst} for src, dst in transitions],
                "functions": {}
            }
        ]
    }

    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON saved to {output_json}")
