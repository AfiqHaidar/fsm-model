import os
import json
from machine_model.narcoleptic_superhero import NarcolepticSuperhero
from machine_model.base import Base


class MachineFactory:

    @staticmethod
    def build_machines():
        machines = []
        machine_sources = MachineFactory.get_source()

        for config_data in machine_sources:
            for machine_type, machines_config in config_data.items():
                if isinstance(machines_config, list):
                    for machine_config in machines_config:
                        name = machine_config.get("name")
                        initial_state = machine_config.get("initial_state")
                        states = machine_config.get("states")
                        transitions = machine_config.get("transitions")
                        functions = machine_config.get("functions")
                        triggers = machine_config.get("triggers")

                        machine = MachineFactory.create_machine(
                            machine_type, name, initial_state, states, transitions, functions, triggers)
                        if machine:
                            machines.append(machine)

        return machines

    @staticmethod
    def get_source():
        json_data_list = []
        for filename in os.listdir('machine_source'):
            if filename.endswith('.json'):
                file_path = os.path.join('machine_source', filename)

                with open(file_path, 'r') as file:
                    try:
                        config_data = json.load(file)
                        json_data_list.append(config_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON file: {filename}")
                    except Exception as e:
                        print(f"Error reading file {filename}: {e}")

        return json_data_list

    @staticmethod
    def create_machine(machine_type, name, initial_state, states, transitions, functions, triggers):
        if machine_type == "NarcolepticSuperheroes":
            return NarcolepticSuperhero(name, states, transitions, functions, initial_state)

        return Base(name, states, transitions, functions, initial_state)
