import numpy as np
from parameters import RiderParameters

class Rider:
    ID = 0

    def calculate_valuation(self, params: RiderParameters):
        # TODO - add more complex valuation logic here
        return np.random.normal(params.init_valuation_mean, params.init_valuation_std)

    def __init__(self, params: RiderParameters):
        self.id = Rider.ID
        Rider.ID += 1

        self.valuation = self.calculate_valuation(params)
