from dataclasses import dataclass, replace

@dataclass(frozen=True)
class SurgeParameters:
    def update(self, **kwargs):
        return replace(self, **kwargs)

@dataclass(frozen=True)
class AuctionParameters:
    reserve_price: float
    lambda_param: float

    def update(self, **kwargs):
        return replace(self, **kwargs)
    
@dataclass(frozen=True)
class RiderParameters:
    init_valuation_mean: float # Normal distribution parameter
    init_valuation_std: float # Normal distribution parameter

    dist_mean: float # Normal distribution parameter for travel time/distance
    dist_std: float # Normal distribution parameter


    def update(self, **kwargs):
        return replace(self, **kwargs)
    
@dataclass(frozen=True)
class Parameters:
    surge: SurgeParameters
    auction: AuctionParameters
    rider: RiderParameters

    num_drivers: int
    average_riders_per_minute: float # Poisson distribution parameter
    time_steps: int
    
    def update(self, **kwargs):
        return replace(self, **kwargs)