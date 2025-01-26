import random


def random_state_simulation(machine):
    print(f"\n<RANDOM> Testing machine: {machine.name}")

    initial_state = machine.state

    while True:
        print(f"\nCurrent State: {machine.state}")

        triggers = machine.machine.get_triggers(machine.state)

        if not triggers:
            print("No triggers available, stopping.")
            break

        trigger = random.choice(triggers)
        while trigger.startswith("to_"):
            trigger = random.choice(triggers)

        print(f" Available : {triggers}\n  Triggering: {trigger}")

        machine.trigger(trigger)

        print(f"   New State: {machine.state}")

        if machine.state == initial_state:
            print("Returned to initial state, stopping iteration.")
            break
