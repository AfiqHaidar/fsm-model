from machine_simulation.random_state_simulation import random_state_simulation
from machine_simulation.path_state_simulation import path_state_simulation
from machine_simulation.graph_simulation import GraphSimulation
import os


def run_random_simulation(machine):
    machine.set_state(state=machine.initial_state)
    random_state_simulation(machine)


def run_path_simulation(machine):
    machine.show_states()
    source_state = input("Enter the source state: ")
    dest_state = input("Enter the destination state: ")
    machine.set_state(state=source_state)
    path_state_simulation(machine, source_state, dest_state)


def run_graph_simulation(machine):
    directory = 'machine_graph'
    graph_path = os.path.join(directory, f'{machine.name}.png')
    machine.machine.get_graph().draw(graph_path, prog='dot')

    viewer = GraphSimulation(graph_path)
    viewer.mainloop()
