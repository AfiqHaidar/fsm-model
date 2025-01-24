import random
from transitions import Machine
from transitions.extensions import GraphMachine


class NarcolepticSuperhero(object):

    def __init__(self, name, states, transitions, functions, initial_state):
        self.name = name
        self.states = states
        self.initial_state = initial_state
        self.kittens_rescued = 0
        self.machine = GraphMachine(model=self, states=states,
                                    initial=initial_state, auto_transitions=True, show_conditions=True)

        for transition in transitions:
            trigger = transition["trigger"]
            source = transition["source"]
            dest = transition["dest"]
            before = transition.get("before")
            after = transition.get("after")
            conditions = transition.get("conditions")

            if before:
                self.machine.add_transition(
                    trigger, source, dest, before=getattr(self, before))
            elif after:
                self.machine.add_transition(
                    trigger, source, dest, after=getattr(self, after))
            elif conditions:
                if isinstance(conditions, str):
                    conditions = [conditions]
                self.machine.add_transition(
                    trigger, source, dest, conditions=conditions)
            else:
                self.machine.add_transition(trigger, source, dest)

        for func_name, func in functions.items():
            if callable(func):
                setattr(self, func_name, func)

    def update_journal(self):
        self.kittens_rescued += 1

    @property
    def is_exhausted(self):
        return False if random.random() < 0.5 else False

    def change_into_super_secret_costume(self):
        # print("Beauty, eh?")
        return

    def change_into_heroine_costume(self):
        # print("Ready to save the city!")
        return

    def show_states(self):
        print(f"\nStates for {self.name}:")
        for state in self.states:
            print(f"- {state}")
        print("")

    def set_state(self, state):
        goto_state = f"to_{state}"
        if hasattr(self, goto_state):
            set = getattr(self, goto_state)
            set()
