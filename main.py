from factory import MachineFactory
from runner import run_random_simulation, run_path_simulation, run_graph_simulation

def choose_machine(machines):
    # Display machine options
    print("\nAvailable Machines:")
    for idx, machine in enumerate(machines, 1):
        print(f"{idx}. {machine.name} (Initial State: {machine.state})")
    print("0. Exit")

    # Get user choice
    while True:
        try:
            choice = int(input("\nChoose a machine (0 to exit): "))
            if choice == 0:
                return None  # Exit option
            elif 1 <= choice <= len(machines):
                return machines[choice - 1]  # Return selected machine
            else:
                print("Invalid choice. Please select a valid machine.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def choose_simulation():
    # Menu to choose simulation type
    print("\nChoose simulation type:")
    print("1. Random State Simulation")
    print("2. Path Simulation")
    print("3. Graph Simulation")
    print("0. Back to machine selection")

    while True:
        try:
            choice = int(input("\nChoose an option (0 to go back): "))
            if choice == 0:
                return None  # Go back to machine selection
            elif choice == 1:
                return "random"
            elif choice == 2:
                return "path"
            elif choice == 3:
                return "graph"
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def run_machine_simulation(machine):
    while True:
        # Choose the simulation
        simulation_type = choose_simulation()

        if simulation_type is None:
            return  # Back to machine selection

        if simulation_type == "random":
            run_random_simulation(machine)

        elif simulation_type == "path":
            run_path_simulation(machine)

        elif simulation_type == "graph":
            run_graph_simulation(machine)


def main():
    machines = MachineFactory.build_machines()

    if not machines:
        print("No machines were built.")
        return

    while True:
        # Choose the machine
        selected_machine = choose_machine(machines)

        if selected_machine is None:
            print("Exiting program...")
            break  # Exit the program

        # Run simulations for the chosen machine
        run_machine_simulation(selected_machine)


if __name__ == "__main__":
    main()
