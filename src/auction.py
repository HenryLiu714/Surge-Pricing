from parameters import AuctionParameters, Parameters
from base import Driver, Rider
import numpy as np

class AuctionSimulation:
    def __init__(self, params: Parameters):
        self.params: AuctionParameters = params.surge
        self.rider_params = params.rider

        self.num_drivers = params.num_drivers
        self.average_riders_per_minute = params.average_riders_per_minute

        self.riders: list[Rider] = [] # set of currently waiting riders
        self.available_drivers: list[Driver] = [] # set of currently available drivers
        self.busy_drivers: list[Driver] = [] # set of currently busy drivers

        self.social_surplus = 0
        self.revenue_surplus = 0
        self.total_trips = 0

    def _opportunity_cost(self, rider: Rider):
        # TODO - add more complex opportunity cost logic here, potentially incorporating driver preferences and expected future demand
        return rider.valuation
    
    def _price_generation(self, rider: Rider, opportunity_cost: float):
        # Get the price that would result in the opportunity cost
        # TODO
        return self.params.base_fare + self.params.per_minute_rate * rider.travel_time
    
    def start(self):
        print("Auction Simulation started.")

        # 1. Initialize drivers
        for _ in range(self.num_drivers):
            new_driver = Driver()
            self.available_drivers.append(new_driver)

    def next_step(self):
        print("Moving to the next step of the auction simulation.")

        # 1. Reduce all drivers time to completion by 1, and move any that are now free to the available_drivers set
        for driver in self.busy_drivers:
            driver.update_status(1)
            if driver.is_available():
                self.available_drivers.append(driver)
                self.busy_drivers.remove(driver) # Verify that this works

        print(f"Available drivers: {len(self.available_drivers)}, Busy drivers: {len(self.busy_drivers)}")

        # 2. Generate new riders based on the average_riders_per_minute parameter
        num_new_riders = max(0,np.random.poisson(self.average_riders_per_minute))

        # Treat new riders + remaining riders as a single pool to be matched with drivers, and generate surge price based on this pool
        remaining_riders = len(self.riders)
        self.riders = []

        for _ in range(num_new_riders + remaining_riders):
            new_rider = Rider(self.rider_params)
            self.riders.append(new_rider)

        print(f"Riders: {[(r.id, r.valuation) for r in self.riders]}")

        # 3. Rank riders by opportunity cost
        ranked_riders = sorted(self.riders, key=lambda r: self._opportunity_cost(r), reverse=True)

        # 4. Calculate the price for each rider, and match with drivers if the price is above the reserve price
        num_available_drivers = len(self.available_drivers)

        for rider in ranked_riders[:num_available_drivers]:
            price = self.params.reserve_price
            if num_available_drivers < len(ranked_riders):
                price = self._price_generation(rider, self._opportunity_cost(ranked_riders[num_available_drivers]))

            if price >= self.params.reserve_price:
                # Match with a driver
                driver = self.available_drivers.pop(0)
                driver.accept(rider)
                self.busy_drivers.append(driver)

                # Update surpluses and total trips
                self.social_surplus += rider.valuation - price
                self.revenue_surplus += price
                self.total_trips += 1

                print(f"Rider {rider.id} matched with Driver {driver.id} at price {price}.")