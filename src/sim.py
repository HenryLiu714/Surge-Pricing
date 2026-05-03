from surge import SurgeSimulation
from parameters import Parameters

class Simulation:
    def __init__(self, max_steps, params: Parameters):
        self.max_steps = max_steps
        self.current_step = 0

        self.surge_simulation = SurgeSimulation(params) # Placeholder for now, will add more complex simulation logic later

    def start(self):
        print("Simulation started.")

        self.surge_simulation.start()

    def next_step(self):
        print("Moving to the next step of the simulation.")  

        self.surge_simulation.next_step()
