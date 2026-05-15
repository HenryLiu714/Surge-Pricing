from parameters import Parameters, SurgeParameters, AuctionParameters, RiderParameters
from sim import Simulation

if __name__ == "__main__":
    params = Parameters(
        surge=SurgeParameters(
        ),
        auction=AuctionParameters(
            reserve_price=5.0
        ),
        rider=RiderParameters(
            init_valuation_mean=10,
            init_valuation_std=2,
            dist_mean=10,
            dist_std=2
        ),
        num_drivers=5,
        average_riders_per_minute=5,
        time_steps=5
    )

    sim = Simulation(params=params)
    sim.run()

    # Output
    print(f"Total trips: {sim.surge_simulation.total_trips}")
    print(f"Total social surplus: {sim.surge_simulation.social_surplus}")
    print(f"Total revenue surplus: {sim.surge_simulation.revenue_surplus}")
    print(f"Average social surplus: {sim.surge_simulation.social_surplus / params.time_steps if params.time_steps > 0 else 0}")
    print(f"Average revenue surplus: {sim.surge_simulation.revenue_surplus / params.time_steps if params.time_steps > 0 else 0}")

    print(f"Total trips: {sim.auction_simulation.total_trips}")
    print(f"Total social surplus: {sim.auction_simulation.social_surplus}")
    print(f"Total revenue surplus: {sim.auction_simulation.revenue_surplus}")
    print(f"Average social surplus: {sim.auction_simulation.social_surplus / params.time_steps if params.time_steps > 0 else 0}")
    print(f"Average revenue surplus: {sim.auction_simulation.revenue_surplus / params.time_steps if params.time_steps > 0 else 0}")