import os
from processor import generate_json
from factory import MachineFactory
from runner import run_random_simulation, run_path_simulation, run_graph_simulation
from script.domain import domain_extract
from script.dynamic import dynamic_extract
from script.url import url_extract


# ==== CONSTANTS ====
RAW_DATA_DIR = "raw_data/"
OUTPUT_DIR = "machine_source/"
SCRIPT_OPTIONS = {
    "1": ("Domain-Based Extraction", domain_extract, "domain"),
    "2": ("URL-Based Extraction", url_extract, "url"),
    "3": ("Dynamic Extraction", dynamic_extract, "dynamic"),
}
MENU_OPTIONS = {
    "1": "machines",
    "2": "sources",
    "0": None
}
SIMULATION_OPTIONS = {
    "1": "random",
    "2": "path",
    "3": "graph",
    "0": None
}

# ==== MENU FUNCTIONS ====


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Generate Machines")
        print("2. Generate Sources")
        print("0. Exit")

        choice = input("\nChoose an option (0 to exit): ")
        if choice in MENU_OPTIONS:
            return MENU_OPTIONS[choice]
        print("Invalid choice. Please select a valid option.")


def choose_machine(machines):
    print("\nAvailable Machines:")
    for idx, machine in enumerate(machines, 1):
        print(f"{idx}. {machine.name} (Initial State: {machine.state})")
    print("0. Back to Main Menu")

    while True:
        choice = input("\nChoose a machine (0 to go back): ")
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(machines):
            return machines[int(choice) - 1]
        print("Invalid choice. Please select a valid machine.")


def choose_simulation():
    print("\nChoose simulation type:")
    print("1. Random State Simulation")
    print("2. Path Simulation")
    print("3. Graph Simulation")
    print("0. Back to Machine Selection")

    choice = input("\nChoose an option (0 to go back): ")
    return SIMULATION_OPTIONS.get(choice, None)


def choose_csv():
    csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".csv")]
    if not csv_files:
        print("No CSV files found in raw_data directory.")
        return None

    while True:
        print("\nAvailable CSV Files:")
        for idx, file in enumerate(csv_files, 1):
            print(f"{idx}. {file}")
        print("0. Back to Main Menu")

        choice = input("\nChoose a CSV file (0 to go back): ")
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
            return os.path.join(RAW_DATA_DIR, csv_files[int(choice) - 1])
        print("Invalid choice. Please select a valid file.")


def choose_extractor():
    while True:
        print("\nChoose an extraction method:")
        for key, (desc, _, _) in SCRIPT_OPTIONS.items():
            print(f"{key}. {desc}")
        print("0. Back to CSV Selection")

        choice = input("\nEnter your choice (0 to go back): ")
        if choice == "0":
            return None
        if choice in SCRIPT_OPTIONS:
            return SCRIPT_OPTIONS[choice]
        print("Invalid choice. Please select a valid option.")

# ==== CORE FUNCTIONS ====


def run_machine_simulation(machine):
    while True:
        simulation_type = choose_simulation()
        if simulation_type is None:
            return
        if simulation_type == "random":
            run_random_simulation(machine)
        elif simulation_type == "path":
            run_path_simulation(machine)
        elif simulation_type == "graph":
            run_graph_simulation(machine)


def generate_source():
    while True:
        csv_file = choose_csv()
        if csv_file is None:
            return

        extractor_choice = choose_extractor()
        if extractor_choice is None:
            continue

        extractor_name, extract_function, prefix = extractor_choice
        print(f"\nGenerating source using {extractor_name} on {csv_file}...\n")
        generate_json(csv_file, OUTPUT_DIR, extract_function, prefix)


# ==== MAIN FUNCTION ====


def main():
    while True:
        selection = main_menu()
        if selection is None:
            break

        if selection == "machines":
            machines = MachineFactory.build_machines()
            if not machines:
                print("No machines were built.")
                continue

            while True:
                selected_machine = choose_machine(machines)
                if selected_machine is None:
                    break
                run_machine_simulation(selected_machine)

        elif selection == "sources":
            generate_source()


if __name__ == "__main__":
    main()
