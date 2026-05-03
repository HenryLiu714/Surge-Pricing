from parameters import Parameters, SurgeParameters, AuctionParameters, RiderParameters
from sim import Simulation

if __name__ == "__main__":
    params = Parameters(
        surge=SurgeParameters(
            base_fare=2.0,
            per_minute_rate=0.5,
            surge_multiplier=1.5
        ),
        auction=AuctionParameters(
            reserve_price=5.0,
            bid_increment=0.5
        ),
        rider=RiderParameters(
            init_valuation_mean=10,
            init_valuation_std=2,
            dist_mean=10,
            dist_std=2
        ),
        num_drivers=5,
        average_riders_per_minute=5
    )

    sim = Simulation(max_steps=5, params=params)
    sim.start()

    for _ in range(sim.max_steps):
        sim.next_step()

    # Output
    print(f"Total trips: {sim.surge_simulation.total_trips}")
    print(f"Total social surplus: {sim.surge_simulation.social_surplus}")
    print(f"Total revenue surplus: {sim.surge_simulation.revenue_surplus}")