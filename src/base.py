import numpy as np
from parameters import RiderParameters

class Rider:
    ID = 0

    def calculate_valuation(self, params: RiderParameters):
        # TODO - add more complex valuation logic here, valuation dependent on demand
        return max(0.0, np.random.normal(params.init_valuation_mean, params.init_valuation_std))

    def __init__(self, params: RiderParameters):
        self.id = Rider.ID
        Rider.ID += 1

        self.valuation = self.calculate_valuation(params)
        self.travel_time = int(max(1, np.random.normal(params.dist_mean, params.dist_std))) # Ensure travel time is positive

    def update_valuation(self, params: RiderParameters):
        self.valuation = self.calculate_valuation(params)

class Driver:
    ID = 0

    def __init__(self):
        self.id = Driver.ID
        Driver.ID += 1

        self.status = "FREE" # Free or Busy
        self.time_until_free = 0 # Time until the driver becomes free (if currently busy)

    def update_status(self, time_step):
        if self.status == "BUSY":
            self.time_until_free -= time_step
            if self.time_until_free <= 0:
                self.status = "FREE"
                self.time_until_free = 0

    def is_available(self):
        return self.status == "FREE" 
    
    def accept(self, rider):
        self.status = "BUSY"
        self.time_until_free = rider.travel_time
        return True # Placeholder for now, will add more complex acceptance logic later