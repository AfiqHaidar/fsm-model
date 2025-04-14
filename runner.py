from machine_simulation.random_state_simulation import random_state_simulation
from machine_simulation.path_state_simulation import path_state_simulation
from machine_simulation.max_depth_path_simulation import max_depth_path_simulation
from machine_simulation.graph_simulation import GraphSimulation
import os


def run_random_simulation(machine):
    machine.set_state(state=machine.initial_state)
    random_state_simulation(machine)


def run_path_simulation(machine):
    machine.show_states()

    # Display numbered list of states for source selection
    print("\nSelect source state:")
    for idx, state in enumerate(machine.states, 1):
        print(f"{idx}. {state}")

    # Get source state by number
    while True:
        source_choice = input("\nEnter source state number: ")
        if source_choice.isdigit() and 1 <= int(source_choice) <= len(machine.states):
            source_state = machine.states[int(source_choice) - 1]
            break
        print("Invalid choice. Please select a valid state number.")

    # Display numbered list of states for destination selection
    print("\nSelect destination state:")
    for idx, state in enumerate(machine.states, 1):
        print(f"{idx}. {state}")

    # Get destination state by number
    while True:
        dest_choice = input("\nEnter destination state number: ")
        if dest_choice.isdigit() and 1 <= int(dest_choice) <= len(machine.states):
            dest_state = machine.states[int(dest_choice) - 1]
            break
        print("Invalid choice. Please select a valid state number.")

    # Set machine to source state and run path simulation
    machine.set_state(state=source_state)
    print(f"\nFinding paths from '{source_state}' to '{dest_state}'...")
    path_state_simulation(machine, source_state, dest_state)


def run_graph_simulation(machine):
    directory = 'machine_graph'
    graph_path = os.path.join(directory, f'{machine.name}.png')
    machine.machine.get_graph().draw(graph_path, prog='dot')

    viewer = GraphSimulation(graph_path)
    viewer.mainloop()


def run_max_depth_simulation(machine):
    """
    Function to get the destination state and max depth, then run the max depth path simulation.
    This simulation finds all possible paths to a destination state within a maximum depth.
    """
    machine.show_states()

    # Display numbered list of states for destination selection
    print("\nSelect destination state:")
    for idx, state in enumerate(machine.states, 1):
        print(f"{idx}. {state}")

    # Get destination state by number
    while True:
        dest_choice = input("\nEnter destination state number: ")
        if dest_choice.isdigit() and 1 <= int(dest_choice) <= len(machine.states):
            dest_state = machine.states[int(dest_choice) - 1]
            break
        print("Invalid choice. Please select a valid state number.")

    # Get maximum depth for the search
    while True:
        max_depth_input = input("\nEnter maximum search depth: ")
        if max_depth_input.isdigit() and int(max_depth_input) > 0:
            max_depth = int(max_depth_input)
            break
        print("Invalid choice. Please enter a positive integer for the maximum depth.")

    # Run max depth path simulation
    print(
        f"\nFinding all paths to '{dest_state}' within max depth of {max_depth}...")
    max_depth_path_simulation(machine, dest_state, max_depth)
