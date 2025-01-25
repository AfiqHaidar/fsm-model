
def path_state_simulation(machine, source_state, dest_state):
    all_paths = []
    print(f"\n<PATH> Testing machine: {machine.name}")

    def dfs(current_state, path, visited):
        if current_state in visited:
            return

        if current_state == dest_state:
            all_paths.append(path)
            return

        visited.add(current_state)

        triggers = machine.machine.get_triggers(current_state)
        for trigger in triggers:
            if trigger.startswith("to_"):
                continue
            prev_state = machine.state

            machine.trigger(trigger)
            next_state = machine.state

            dfs(next_state, path + [next_state], visited)

            revert_method = f"to_{prev_state}"
            if hasattr(machine, revert_method):
                revert_func = getattr(machine, revert_method)
                revert_func()

        visited.remove(current_state)

    dfs(source_state, [source_state], set())

    if all_paths:
        print(f"All paths from '{source_state}' to '{dest_state}':")
        for path in all_paths:
            print(" -> ".join(path))
    else:
        print(f"No paths found from '{source_state}' to '{dest_state}'.")
