
class Simulation:
    def __init__(self, max_steps):
        self.max_steps = max_steps
        self.current_step = 0

    def start(self):
        print("Simulation started.")

    def next_step(self):
        print("Moving to the next step of the simulation.")  