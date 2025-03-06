import csv
import json
import os
import re
from urllib.parse import urlparse
from datetime import datetime

# ==== CONSTANTS ====
DELIMITER = ","
FILTER_SOURCE = "WEBHIST"


def extract_url(message):
    url_match = re.search(r"https?://[^\s]+", message)
    if url_match:
        url = url_match.group(0)
        parsed_url = urlparse(url)

        clean_url = parsed_url.netloc + parsed_url.path

        return clean_url.replace("://", "")

    return None


def extract_states_and_transitions(input_csv):
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

            url = extract_url(message)
            if not url:
                continue

            parsed_url = urlparse(url)
            state = parsed_url.scheme + \
                parsed_url.netloc + parsed_url.path

            if state and state not in states:
                states.append(state)

            if previous_state and state and previous_state != state:
                transitions.add((previous_state, state))

            previous_state = state

    return states, sorted(transitions)


def generate_json(input_csv, output_dir):
    """Generate a JSON source file from a given CSV file."""
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json = os.path.join(output_dir, f"url_{current_time}.json")

    states, transitions = extract_states_and_transitions(input_csv)

    json_data = {
        "WebActivityMachine": [
            {
                "name": f"URL_{current_time}",
                "initial_state": states[0] if states else "unknown",
                "states": states,
                "triggers": ["next"],
                "transitions": [{"trigger": "next", "source": src, "dest": dst} for src, dst in transitions],
                "functions": {}
            }
        ]
    }

    os.makedirs(output_dir, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON saved to {output_json}")
