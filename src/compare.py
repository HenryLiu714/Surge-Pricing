"""
compare.py
----------
Compares the auction mechanism (with optimized c(t, t')) against
surge pricing under identical parameters, across multiple simulation runs.

Run with:
    python compare.py
"""

import numpy as np
import matplotlib.pyplot as plt
from parameters import Parameters, SurgeParameters, AuctionParameters, RiderParameters
from auction import AuctionSimulation
from surge import SurgeSimulation

# ── Optimized coefficients from SGD ────────────────────────────────────────
# c(t, t') = -0.8838 + 5.4342t - 1.4419t' - 3.7928t^2 - 0.7461tt' + 1.5715t'^2
BEST_COEFFS = np.array([-0.8838, 5.4342, -1.4419, -3.7928, -0.7461, 1.5715])
ZERO_COEFFS = np.zeros(6)

# ── Parameters ──────────────────────────────────────────────────────────────
params = Parameters(
    surge=SurgeParameters(),
    auction=AuctionParameters(
        reserve_price=1.0,
        lambda_param=1,
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

T        = 50
N_RUNS   = 200


# ── Run simulations ─────────────────────────────────────────────────────────

def run_auction(coeffs, params, T):
    sim = AuctionSimulation(params, coeffs)
    sim.start()
    for _ in range(T):
        sim.next_step()
    return sim.revenue_surplus / T, sim.social_surplus / T, sim.total_trips


def run_surge(params, T):
    sim = SurgeSimulation(params)
    sim.start()
    for _ in range(T):
        sim.next_step()
    return sim.revenue_surplus / T, sim.social_surplus / T, sim.total_trips


print(f"Running {N_RUNS} runs each — auction (optimized), auction (c=0), surge pricing...\n")

auction_opt_revenue, auction_opt_social, auction_opt_trips   = [], [], []
auction_zero_revenue, auction_zero_social, auction_zero_trips = [], [], []
surge_revenue, surge_social, surge_trips                      = [], [], []

for i in range(N_RUNS):
    if (i + 1) % 20 == 0:
        print(f"  Run {i+1}/{N_RUNS}...")

    r, s, t = run_auction(BEST_COEFFS, params, T)
    auction_opt_revenue.append(r)
    auction_opt_social.append(s)
    auction_opt_trips.append(t)

    r, s, t = run_auction(ZERO_COEFFS, params, T)
    auction_zero_revenue.append(r)
    auction_zero_social.append(s)
    auction_zero_trips.append(t)

    r, s, t = run_surge(params, T)
    surge_revenue.append(r)
    surge_social.append(s)
    surge_trips.append(t)


# ── Print summary ───────────────────────────────────────────────────────────

from scipy import stats

def summary(name, rev, soc, trips):
    print(f"\n{name}")
    print(f"  Revenue per round : mean={np.mean(rev):.2f}, std={np.std(rev):.2f}")
    print(f"  Social surplus    : mean={np.mean(soc):.2f}, std={np.std(soc):.2f}")
    print(f"  Total trips       : mean={np.mean(trips):.2f}, std={np.std(trips):.2f}")

summary("Auction (optimized c(t,t'))", auction_opt_revenue, auction_opt_social, auction_opt_trips)
summary("Auction (c=0)",               auction_zero_revenue, auction_zero_social, auction_zero_trips)
summary("Surge pricing",               surge_revenue,        surge_social,        surge_trips)

# pairwise t-tests: optimized auction vs surge
t_rev, p_rev = stats.ttest_ind(auction_opt_revenue, surge_revenue)
t_soc, p_soc = stats.ttest_ind(auction_opt_social,  surge_social)
print(f"\nAuction (opt) vs Surge — revenue : t={t_rev:.3f}, p={p_rev:.4f}")
print(f"Auction (opt) vs Surge — social  : t={t_soc:.3f}, p={p_soc:.4f}")


# ── Plot ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Auction vs Surge Pricing — Revenue and Social Surplus Comparison",
             fontsize=13)

labels  = ["Auction\n(optimized)", "Auction\n(c=0)", "Surge\npricing"]
colors  = ["crimson", "steelblue", "seagreen"]

# Panel 1 — revenue distributions
ax = axes[0]
data_rev = [auction_opt_revenue, auction_zero_revenue, surge_revenue]
bp = ax.boxplot(data_rev, patch_artist=True, widths=0.5)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(labels)
ax.set_ylabel("Avg revenue per round")
ax.set_title("Revenue per round")

# Panel 2 — social surplus distributions
ax = axes[1]
data_soc = [auction_opt_social, auction_zero_social, surge_social]
bp = ax.boxplot(data_soc, patch_artist=True, widths=0.5)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(labels)
ax.set_ylabel("Avg social surplus per round")
ax.set_title("Social surplus per round")

# Panel 3 — total trips
ax = axes[2]
data_trips = [auction_opt_trips, auction_zero_trips, surge_trips]
bp = ax.boxplot(data_trips, patch_artist=True, widths=0.5)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(labels)
ax.set_ylabel("Total trips completed")
ax.set_title("Total trips per simulation")

plt.tight_layout()
plt.savefig("comparison_auction_vs_surge.png", dpi=150, bbox_inches='tight')
print("\nFigure saved to comparison_auction_vs_surge.png")