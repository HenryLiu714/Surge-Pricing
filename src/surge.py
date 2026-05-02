from parameters import SurgeParameters

class SurgeSimulation:
    def __init__(self, params: SurgeParameters):
        self.params = params

        self.riders = set() # Set of unique 

    def start(self):
        print("Surge Simulation started.")

    def update_params(self, new_params):
        print(f"Updating surge parameters to: {new_params}")

    def next_step(self):
        print("Moving to the next step of the surge simulation.")