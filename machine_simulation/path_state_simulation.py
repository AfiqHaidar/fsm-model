def path_state_simulation(machine, source_state, dest_state):
    import os
    import json

    all_paths = []
    debug_enabled = True  # Set to False to disable detailed debug output
    path_counter = 0
    transition_counter = 0

    print(f"\n<PATH> Testing machine: {machine.name}")
    print(f"Finding paths from '{source_state}' to '{dest_state}'")

    # First attempt: Extract transitions from the JSON configuration if possible
    transitions_map = {}
    json_file_loaded = False

    # Look for machine configuration in JSON file
    json_filename = f"{machine.name}.json"
    parts = machine.name.rsplit("_", 2)
    prefix = parts[0]
    json_paths = [
        json_filename,
        os.path.join("machine_source", prefix, json_filename),
    ]

    for json_path in json_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    print(f"Found and loading transitions from: {json_path}")
                    data = json.load(f)

                    # Look for a machine definition that matches our machine name
                    for category, machines in data.items():
                        if isinstance(machines, list):
                            for machine_data in machines:
                                if machine_data.get("name") == machine.name:
                                    # Found the machine configuration!
                                    print(
                                        f"Found machine definition in category '{category}'")

                                    # Extract transitions
                                    for t in machine_data.get("transitions", []):
                                        source = t.get("source")
                                        trigger = t.get("trigger")
                                        dest = t.get("dest")

                                        # Skip wildcards
                                        if source == "*":
                                            continue

                                        # Add this transition to our map
                                        if source not in transitions_map:
                                            transitions_map[source] = []

                                        # Only add if it's not already there
                                        if (trigger, dest) not in transitions_map[source]:
                                            transitions_map[source].append(
                                                (trigger, dest))

                                    json_file_loaded = True
                                    break
                        if json_file_loaded:
                            break
                if json_file_loaded:
                    break
            except Exception as e:
                print(f"Error loading JSON from {json_path}: {e}")

    if debug_enabled:
        print("\nTransition map:")
        for state, transitions in sorted(transitions_map.items()):
            if transitions:
                print(f"  From '{state}' can go to:")
                for trigger, dest in sorted(transitions):
                    print(f"    '{dest}' via '{trigger}'")

    def dfs(current_state, path, visited_transitions, depth=0):
        nonlocal path_counter, transition_counter
        indent = "  " * depth

        if debug_enabled:
            print(
                f"\n{indent}[DEPTH {depth}] Exploring from state: '{current_state}'")
            print(f"{indent}Current path: {' -> '.join(path)}")

        # If we've reached the destination state, add this path to our collection
        if current_state == dest_state:
            path_counter += 1
            print(f"\n{indent}✅ PATH FOUND #{path_counter}: {' -> '.join(path)}")
            all_paths.append(path[:])
            return

        # Get all available transitions for the current state
        available_transitions = transitions_map.get(current_state, [])

        if debug_enabled:
            if available_transitions:
                print(f"{indent}Available transitions:")
                for trigger, dest in sorted(available_transitions):
                    print(f"{indent}  '{trigger}' can lead to: '{dest}'")
            else:
                print(
                    f"{indent}No transitions available from state '{current_state}'")

        if not available_transitions:
            print(
                f"{indent}❌ DEAD END: No valid transitions available from state '{current_state}'")
            return

        # Try each transition
        for trigger, next_state in sorted(available_transitions):
            transition_counter += 1

            if debug_enabled:
                print(
                    f"{indent}[Attempt #{transition_counter}] Examining transition: '{current_state}' --[{trigger}]--> '{next_state}'")

            # Skip if this would create a cycle in our current path
            if next_state in path:
                if debug_enabled:
                    print(
                        f"{indent}  ⚠️ State '{next_state}' would create a cycle in path - skipping")
                continue

            # Create a path signature to avoid duplicate explorations
            path_sig = (current_state, trigger, next_state)
            if path_sig in visited_transitions:
                if debug_enabled:
                    print(
                        f"{indent}  ⚠️ Path segment '{current_state}' --[{trigger}]--> '{next_state}' already explored")
                continue

            # Mark this path segment as visited
            visited_transitions.add(path_sig)

            if debug_enabled:
                print(
                    f"{indent}  👉 Recursing deeper with new path: {' -> '.join(path + [next_state])}")

            # Set the machine to the next state for exploration
            current_machine_state = machine.state
            machine.set_state(next_state)

            # Recursively explore from this new state
            dfs(next_state, path + [next_state],
                visited_transitions, depth + 1)

            if debug_enabled:
                print(
                    f"{indent}  ⬅️ Returned from recursion to state '{current_state}'")

            # Always revert back to the current state after exploration
            machine.set_state(current_state)

    # Start DFS from the source state
    print("\nStarting path search...")
    machine.set_state(source_state)
    dfs(source_state, [source_state], set())

    # Display results summary
    print("\n" + "="*50)
    print(
        f"SEARCH COMPLETE: Attempted {transition_counter} transition explorations")

    if all_paths:
        print(
            f"\nFound {len(all_paths)} path(s) from '{source_state}' to '{dest_state}':")
        for i, path in enumerate(all_paths, 1):
            path_str = " -> ".join(path)
            print(f"Path {i}: {path_str}")

            # Print triggers used for each step
            if debug_enabled:
                print("  Triggers used:")
                for j in range(len(path) - 1):
                    src = path[j]
                    dst = path[j+1]
                    # Find which trigger was used for this transition
                    trigger_used = None
                    for src_transitions in transitions_map.get(src, []):
                        t, d = src_transitions
                        if d == dst:
                            trigger_used = t
                            break
                    print(f"    {src} --[{trigger_used}]--> {dst}")
    else:
        print(f"\nNo paths found from '{source_state}' to '{dest_state}'.")

    # Make sure to reset the machine to the source state when done
    machine.set_state(source_state)
    print(f"Machine reset to state: '{source_state}'")
    print("="*50)
