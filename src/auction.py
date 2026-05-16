from parameters import Parameters
from base import Driver, Rider
import numpy as np


def poly_cost(t: int, t_prime: float, coeffs: np.ndarray) -> float:
    a00, a10, a01, a20, a11, a02 = coeffs
    val = (a00
           + a10 * t + a01 * t_prime + a11 * t*t_prime
           + a20 * t**2 + a02* t_prime**2)
    return max(val, val)


class AuctionSimulation:
    def __init__(self, params: Parameters, coeffs: np.ndarray):
        self.params       = params.auction
        self.rider_params = params.rider
        self.num_drivers  = params.num_drivers
        self.avg_riders   = params.average_riders_per_minute
        self.coeffs       = coeffs

        self.available_drivers: list[Driver] = []
        self.busy_drivers:      list[Driver] = []
        self.waiting_riders:    list[Rider]  = []

        self.social_surplus  = 0.0
        self.revenue_surplus = 0.0
        self.total_trips     = 0
        self.current_step    = 0

    def _opportunity_cost(self, rider: Rider) -> float:
        return poly_cost(self.current_step, rider.travel_time, coeffs=self.coeffs)

    def _score(self, rider: Rider) -> float:
        return rider.valuation - self._opportunity_cost(rider)

    def _payment(self, rider: Rider, s_prime: float) -> float:
        return s_prime + self._opportunity_cost(rider)

    def start(self):
        self.available_drivers = [Driver() for _ in range(self.num_drivers)]
        self.busy_drivers      = []
        self.waiting_riders    = []
        self.social_surplus    = 0.0
        self.revenue_surplus   = 0.0
        self.total_trips       = 0
        self.current_step      = 0

    def next_step(self):
        self.current_step += 1

        # Free drivers whose trips have completed
        still_busy = []
        for driver in self.busy_drivers:
            driver.update_status(1)
            if driver.is_available():
                self.available_drivers.append(driver)
            else:
                still_busy.append(driver)
        self.busy_drivers = still_busy

        # Resample valuations of waiting riders and add new arrivals
        for rider in self.waiting_riders:
            rider.update_valuation(self.rider_params)

        num_new = np.random.poisson(self.avg_riders)
        new_riders = [Rider(self.rider_params) for _ in range(num_new)]
        riders = self.waiting_riders + new_riders

        # Score all riders
        scored = [(self._score(r), r) for r in riders]
        eligible = sorted(
            [(s, r) for s, r in scored if s >= 0],
            key=lambda x: x[0],
            reverse=True
        )

        k = len(self.available_drivers)
        s_prime = eligible[k][0] if len(eligible) > k else 0.0

        # Allocate top k eligible riders
        matched_ids = set()
        for score, rider in eligible[:k]:
            payment = self._payment(rider, s_prime)

            driver = self.available_drivers.pop(0)
            driver.accept(rider)
            self.busy_drivers.append(driver)

            self.social_surplus  += rider.valuation - payment
            self.revenue_surplus += payment
            self.total_trips     += 1
            matched_ids.add(rider.id)

        # All unmatched riders persist regardless of eligibility
        self.waiting_riders = [r for r in riders if r.id not in matched_ids]