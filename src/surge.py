from parameters import SurgeParameters, Parameters

from base import Driver, Rider

import numpy as np
from scipy.stats import norm

class SurgeSimulation:
    def __init__(self, params: Parameters):
        self.params: SurgeParameters = params.surge
        self.rider_params = params.rider

        self.num_drivers = params.num_drivers
        self.average_riders_per_minute = params.average_riders_per_minute

        self.riders: list[Rider] = [] # set of currently waiting riders
        self.available_drivers: list[Driver] = [] # set of currently available drivers
        self.busy_drivers: list[Driver] = [] # set of currently busy drivers

        self.social_surplus = 0
        self.revenue_surplus = 0
        self.total_trips = 0

    def _generate_unit_price(self):
        # Generates the market clearing unit price
        num_riders = len(self.riders)
        num_drivers = len(self.available_drivers)

        mu_V = self.rider_params.init_valuation_mean
        sigma_V = self.rider_params.init_valuation_std

        mu_T = self.rider_params.dist_mean
        sigma_T = self.rider_params.dist_std

        # W = V/T, approximated as normal using delta method
        mu_W = mu_V / mu_T
        sigma_W = sigma_V / mu_T  # first-order approximation assuming T is low-variance

        # p* = F_W^{-1}(1 - s / mu_R)
        if num_riders == 0 or num_drivers >= num_riders:
            p_star = 0.0  # or some minimum floor price
        else:
            ratio = num_drivers / num_riders
            p_star = mu_W + sigma_W * norm.ppf(1 - ratio)

        print(f"Generated unit price: {p_star} (num_drivers: {num_drivers}, num_riders: {num_riders})")

        return max(p_star, 0)

    def _generate_price(self, rider: Rider):
        unit_price = self._generate_unit_price()

        # TODO - add more complex price generation logic here, potentially incorporating rider valuation and distance

        return unit_price * rider.travel_time


    def start(self):
        print("Surge Simulation started.")

        # 1. Initialize drivers
        for _ in range(self.num_drivers):
            new_driver = Driver()
            self.available_drivers.append(new_driver)

    def next_step(self):
        print("Moving to the next step of the surge simulation.")

        # 1. Reduce all drivers time to completion by 1, and move any that are now free to the available_drivers set
        still_busy = []
        for driver in self.busy_drivers:
            driver.update_status(1)
            if driver.is_available():
                self.available_drivers.append(driver)
            else:
                still_busy.append(driver)
        self.busy_drivers = still_busy

        print(f"Surge: Available drivers: {len(self.available_drivers)}, Busy drivers: {len(self.busy_drivers)}")

        # 2. Generate new riders based on the average_riders_per_minute parameter
        num_new_riders = max(0,np.random.poisson(self.average_riders_per_minute))

        # Treat new riders + remaining riders as a single pool to be matched with drivers, and generate surge price based on this pool
        remaining_riders = len(self.riders)
        self.riders = []

        for _ in range(num_new_riders + remaining_riders):
            new_rider = Rider(self.rider_params)
            self.riders.append(new_rider)

        # 3. Match riders to drivers based on the surge pricing algorithm (not implemented yet)

        # TODO: Generate surge pricing scheme to calculate unit ride price based on current supply/demand imbalance, and match riders to drivers based on this price and their valuations
        for rider in self.riders:
            price = self._generate_price(rider)
            print(f"Generated price for Rider {rider.id}: {price} (valuation: {rider.valuation})")

            if price > rider.valuation:
                continue # Rider decides not to take the trip at this price

            # For now, just have drivers accept any rider that they are matched with, and match riders to drivers in order of arrival
            if len(self.available_drivers) > 0:
                driver = self.available_drivers.pop()
                driver.accept(rider)

                self.busy_drivers.append(driver)
                self.riders.remove(rider)

                self.total_trips += 1
                self.social_surplus += rider.valuation - price
                self.revenue_surplus += price