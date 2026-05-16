"""
optimize_coefficients.py
------------------------
Finds the degree-2 polynomial opportunity cost c(t, t') that maximises
social revenue in the auction simulation, using stochastic gradient descent
(finite-difference gradient estimates) from multiple random starting points.

Usage:
    from optimize_coefficients import run_optimization
    from parameters import Parameters

    params = Parameters(...)
    best_coeffs, best_revenue = run_optimization(params, T=100)
"""

import numpy as np
import matplotlib.pyplot as plt
from parameters import Parameters
from auction import AuctionSimulation, poly_cost


# ── Evaluation ─────────────────────────────────────────────────────────────

def evaluate(coeffs: np.ndarray,
             params: Parameters,
             T: int,
             num_runs: int = 3) -> float:
    """
    Run the auction simulation num_runs times with the given coefficients.
    Returns average revenue per step across all runs.
    """
    totals = []
    for _ in range(num_runs):
        sim = AuctionSimulation(params, coeffs)
        sim.start()
        for _ in range(T):
            sim.next_step()
        totals.append(sim.revenue_surplus / T)
    return float(np.mean(totals))


# ── Gradient estimation ────────────────────────────────────────────────────

def estimate_gradient(coeffs: np.ndarray,
                      params: Parameters,
                      T: int,
                      epsilon: float = 0.05,
                      num_runs: int = 3) -> np.ndarray:
    """
    Finite-difference gradient estimate.
    Perturbs each coefficient by epsilon and measures revenue change.
    Requires len(coeffs) + 1 simulation evaluations per call.
    """
    grad   = np.zeros_like(coeffs)
    w_base = evaluate(coeffs, params, T, num_runs)
    for k in range(len(coeffs)):
        perturbed     = coeffs.copy()
        perturbed[k] += epsilon
        w_plus        = evaluate(perturbed, params, T, num_runs)
        grad[k]       = (w_plus - w_base) / epsilon
    return grad


# ── SGD optimisation ───────────────────────────────────────────────────────

def optimize_coefficients(params: Parameters,
                          T: int          = 100,
                          num_starts: int = 10,
                          num_steps: int  = 40,
                          lr: float       = 0.05,
                          epsilon: float  = 0.05,
                          eval_runs: int  = 3,
                          seed: int       = 42
                          ) -> tuple[np.ndarray, float, list]:
    """
    SGD with decaying learning rate from multiple random starting points.

    Returns
    -------
    best_coeffs   : np.ndarray, shape (6,)  — optimal [a00,a10,a01,a20,a11,a02]
    best_revenue  : float                   — best average revenue per step
    trajectories  : list of dicts           — full history per starting point
    """
    rng        = np.random.default_rng(seed)
    NUM_COEFFS = 6

    best_revenue = -np.inf
    best_coeffs  = None
    trajectories = []

    for start_idx in range(num_starts):
        coeffs = rng.uniform(0, 2, NUM_COEFFS)

        revenue_history = []
        coeff_history   = [coeffs.copy()]

        for step in range(num_steps):
            lr_t   = lr / np.sqrt(step + 1)
            grad   = estimate_gradient(coeffs, params, T,
                                       epsilon=epsilon, num_runs=eval_runs)
            coeffs = coeffs + lr_t * grad
            coeff_history.append(coeffs.copy())

            w = evaluate(coeffs, params, T, num_runs=eval_runs)
            revenue_history.append(w)

            print(f"  Start {start_idx+1}/{num_starts} | "
                  f"Step {step+1}/{num_steps} | revenue={w:.4f}")

        final_revenue = evaluate(coeffs, params, T, num_runs=10)
        trajectories.append({
            'start_idx':       start_idx,
            'revenue_history': revenue_history,
            'coeff_history':   coeff_history,
            'final_coeffs':    coeffs.copy(),
            'final_revenue':   final_revenue,
        })

        if final_revenue > best_revenue:
            best_revenue = final_revenue
            best_coeffs  = coeffs.copy()
            print(f"  *** New best: revenue={best_revenue:.4f}")

    return best_coeffs, best_revenue, trajectories


# ── Plotting ───────────────────────────────────────────────────────────────

def plot_results(trajectories: list,
                 best_coeffs: np.ndarray,
                 params: Parameters,
                 T: int,
                 save_path: str = 'sgd_results.png'):
    """
    Three-panel figure:
      1. Revenue vs SGD step for each starting point
      2. Learned c(t, t') curves at t=0 for each starting point vs c=0
      3. Revenue distribution: best coeffs vs c=0 baseline
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("SGD Optimisation of Polynomial Opportunity Cost c(t, t')",
                 fontsize=13)

    # Panel 1 — revenue trajectories across SGD steps
    ax = axes[0]
    for traj in trajectories:
        ax.plot(traj['revenue_history'], alpha=0.5, linewidth=1.2)
    ax.set_xlabel("SGD step")
    ax.set_ylabel("Avg revenue per round")
    ax.set_title("Revenue across SGD steps\n(each line = one starting point)")

    # Panel 2 — learned c(t, t') at fixed t=0
    ax = axes[1]
    t_prime_vals = np.linspace(0, 30, 200)
    for traj in trajectories:
        c_vals = [poly_cost(0, tp, traj['final_coeffs']) for tp in t_prime_vals]
        ax.plot(t_prime_vals, c_vals, alpha=0.4, linewidth=1, color='steelblue')
    c_best = [poly_cost(0, tp, best_coeffs) for tp in t_prime_vals]
    ax.plot(t_prime_vals, c_best, color='crimson', linewidth=2, label='Best')
    ax.axhline(0, color='black', linewidth=1, linestyle='--', label='c = 0 baseline')
    ax.set_xlabel("Trip duration t'")
    ax.set_ylabel("c(t=0, t')")
    ax.set_title("Learned opportunity cost\nvs trip duration (at t=0)")
    ax.legend()

    # Panel 3 — revenue distribution: best coeffs vs c=0
    ax = axes[2]
    zero_coeffs = np.zeros(6)
    n_eval = 50

    best_revenues = [
        evaluate(best_coeffs, params, T, num_runs=1)
        for _ in range(n_eval)
    ]
    zero_revenues = [
        evaluate(zero_coeffs, params, T, num_runs=1)
        for _ in range(n_eval)
    ]

    ax.hist(zero_revenues, bins=15, alpha=0.6, color='steelblue', label='c = 0')
    ax.hist(best_revenues, bins=15, alpha=0.6, color='crimson', label="Best c(t, t')")
    ax.axvline(np.mean(zero_revenues), color='steelblue', linestyle='--', linewidth=1.5)
    ax.axvline(np.mean(best_revenues), color='crimson',    linestyle='--', linewidth=1.5)
    ax.set_xlabel("Avg revenue per round")
    ax.set_ylabel("Count")
    ax.set_title("Revenue distribution\nbest c(t, t') vs c = 0 baseline")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to {save_path}")


# ── Entry point ────────────────────────────────────────────────────────────

def run_optimization(params: Parameters,
                     T: int          = 100,
                     num_starts: int = 10,
                     num_steps: int  = 40,
                     lr: float       = 0.05,
                     epsilon: float  = 0.05,
                     eval_runs: int  = 3,
                     save_path: str  = 'sgd_results.png'
                     ) -> tuple[np.ndarray, float]:
    """
    Full pipeline: optimise coefficients then plot results.

    Parameters
    ----------
    params      : simulation parameters
    T           : number of steps per simulation run
    num_starts  : number of random starting points for SGD
    num_steps   : SGD steps per starting point
    lr          : initial learning rate (decays as lr/sqrt(step))
    epsilon     : finite-difference step size for gradient estimation
    eval_runs   : simulation runs per gradient evaluation (reduces noise)
    save_path   : path to save the results figure

    Returns
    -------
    best_coeffs  : optimal [a00, a10, a01, a20, a11, a02]
    best_revenue : best average revenue per step achieved
    """
    print("=== Optimising polynomial opportunity cost c(t, t') via SGD ===\n")

    best_coeffs, best_revenue, trajectories = optimize_coefficients(
        params,
        T=T, num_starts=num_starts, num_steps=num_steps,
        lr=lr, epsilon=epsilon, eval_runs=eval_runs
    )

    print(f"\n=== Optimisation complete ===")
    print(f"Best avg revenue per round : {best_revenue:.4f}")
    print(f"Optimal coefficients       : {best_coeffs}")
    a00, a10, a01, a20, a11, a02 = best_coeffs
    print(f"\nc(t, t') = {a00:.4f}")
    print(f"         + {a10:.4f}·t    + {a01:.4f}·t'")
    print(f"         + {a20:.4f}·t²   + {a11:.4f}·t·t'  + {a02:.4f}·t'²")

    plot_results(trajectories, best_coeffs, params, T, save_path=save_path)

    return best_coeffs, best_revenue

def compare_best_vs_zero(best_coeffs: np.ndarray,
                          params: Parameters,
                          T: int,
                          n_eval: int = 200,
                          save_path: str = 'comparison.png'):
    """
    Rigorously compare best found coefficients against c=0 baseline
    over many runs to determine if the difference is meaningful.
    """
    zero_coeffs = np.zeros(6)

    print(f"\nRunning {n_eval}-run comparison against c=0 baseline...")
    best_revenues = [evaluate(best_coeffs, params, T, num_runs=1) for _ in range(n_eval)]
    zero_revenues = [evaluate(zero_coeffs, params, T, num_runs=1) for _ in range(n_eval)]

    best_mean = np.mean(best_revenues)
    zero_mean = np.mean(zero_revenues)
    best_std  = np.std(best_revenues)
    zero_std  = np.std(zero_revenues)

    # two-sample t-test
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(best_revenues, zero_revenues)

    print(f"  c=0    : mean={zero_mean:.4f}, std={zero_std:.4f}")
    print(f"  best   : mean={best_mean:.4f}, std={best_std:.4f}")
    print(f"  diff   : {best_mean - zero_mean:.4f} ({(best_mean - zero_mean) / zero_mean * 100:.2f}%)")
    print(f"  t-stat : {t_stat:.4f}, p-value : {p_value:.4f}")
    if p_value < 0.05:
        print("  *** Difference is statistically significant (p < 0.05)")
    else:
        print("  Difference is NOT statistically significant — best c(t,t') is equivalent to c=0")

    # plot
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle("Best c(t, t') vs c = 0 baseline — rigorous comparison", fontsize=12)

    ax = axes[0]
    ax.hist(zero_revenues, bins=20, alpha=0.6, color='steelblue', label=f'c=0  (mean={zero_mean:.2f})')
    ax.hist(best_revenues, bins=20, alpha=0.6, color='crimson',   label=f'best (mean={best_mean:.2f})')
    ax.axvline(zero_mean, color='steelblue', linestyle='--', linewidth=1.5)
    ax.axvline(best_mean, color='crimson',   linestyle='--', linewidth=1.5)
    ax.set_xlabel("Avg revenue per round")
    ax.set_ylabel("Count")
    ax.set_title(f"Revenue distributions\n(n={n_eval} runs each)")
    ax.legend()

    ax = axes[1]
    diffs = np.array(best_revenues) - np.array(zero_revenues)
    ax.hist(diffs, bins=20, color='slategray', alpha=0.7)
    ax.axvline(0,             color='black',  linestyle='--', linewidth=1.5, label='no difference')
    ax.axvline(np.mean(diffs), color='crimson', linestyle='--', linewidth=1.5,
               label=f'mean diff={np.mean(diffs):.2f}')
    ax.set_xlabel("Revenue difference (best - zero)")
    ax.set_ylabel("Count")
    ax.set_title(f"Per-run revenue difference\np={p_value:.3f}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Comparison figure saved to {save_path}")

    return best_mean, zero_mean, p_value