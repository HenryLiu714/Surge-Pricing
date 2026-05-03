from surge import SurgeSimulation
from auction import AuctionSimulation
from parameters import Parameters

class Simulation:
    def __init__(self, params: Parameters):
        self.max_steps = params.time_steps
        self.current_step = 0

        self.surge_simulation = SurgeSimulation(params) # Placeholder for now, will add more complex simulation logic later
        self.auction_simulation = AuctionSimulation(params) # Placeholder for now, will add auction simulation logic later

    def start(self):
        print("Simulation started.")

        self.surge_simulation.start()
        self.auction_simulation.start()

    def next_step(self):
        print("Moving to the next step of the simulation.")  

        self.surge_simulation.next_step()
        self.auction_simulation.next_step()

    def run(self):
        self.start()

        for _ in range(self.max_steps):
            self.next_step()
