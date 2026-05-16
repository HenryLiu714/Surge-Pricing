"""
run_optimization.py
-------------------
Runs the SGD optimization to find the best degree-2 polynomial
opportunity cost function c(t, t') for the auction simulation.

Run with:
    python run_optimization.py
"""

from parameters import Parameters, SurgeParameters, AuctionParameters, RiderParameters
from optimize_coefficients import run_optimization, compare_best_vs_zero

if __name__ == "__main__":
    params = Parameters(
        surge=SurgeParameters(),
        auction=AuctionParameters(
            reserve_price=1.0,
            lambda_param=1,      # unused — replaced by polynomial coefficients
        ),
        rider=RiderParameters(
            init_valuation_mean=100.0,
            init_valuation_std=10.0,
            dist_mean=10.0,
            dist_std=2.0,
        ),
        num_drivers=5,
        average_riders_per_minute=5.0,
        time_steps=50,
    )

    best_coeffs, best_revenue = run_optimization(
        params,
        T=50,           # steps per simulation run
        num_starts=10,  # random starting points for SGD
        num_steps=40,   # SGD steps per starting point
        lr=0.05,        # initial learning rate, decays as lr/sqrt(step)
        epsilon=0.05,   # finite difference step for gradient estimation
        eval_runs=3,    # simulation runs per gradient evaluation
        save_path="sgd_results.png",
    )


    compare_best_vs_zero(best_coeffs, params, 50, n_eval=200, save_path='comparison.png')