import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from parameters import Parameters, SurgeParameters, AuctionParameters, RiderParameters
from sim import Simulation


PARAM_DEFS = {
    "Surge": [
        ("base_fare",        "Base Fare ($)",        0.0,  20.0, 0.1,  2.0),
        ("per_minute_rate",  "Per Minute Rate ($/min)", 0.0, 5.0, 0.05, 0.5),
        ("surge_multiplier", "Surge Multiplier",     1.0,  5.0,  0.1,  1.5),
    ],
    "Auction": [
        ("reserve_price",    "Reserve Price ($)",    0.0,  20.0, 0.5,  5.0),
    ],
    "Rider": [
        ("init_valuation_mean", "Valuation Mean ($)", 1.0, 30.0, 0.5, 10.0),
        ("init_valuation_std",  "Valuation Std ($)",  0.1, 10.0, 0.1,  2.0),
        ("dist_mean",           "Distance Mean (min)", 1.0, 30.0, 0.5, 10.0),
        ("dist_std",            "Distance Std (min)",  0.1, 10.0, 0.1,  2.0),
    ],
    "Base": [
        ("num_drivers",               "Number of Drivers",        1,  20,  1,   5),
        ("average_riders_per_minute", "Avg Riders / Minute",      0.1, 20.0, 0.1, 5.0),
        ("time_steps",                "Time Steps",               1,  100,  1,  5),
    ],
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Surge Pricing Simulator")
        self.resizable(True, True)

        self.sliders: dict[str, tk.DoubleVar] = {}

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # Left: parameter panels
        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 12))

        for group, params in PARAM_DEFS.items():
            frame = ttk.LabelFrame(left, text=group, padding=8)
            frame.pack(fill="x", pady=4)
            for key, label, lo, hi, step, default in params:
                self._make_slider(frame, key, label, lo, hi, step, default)

        run_btn = ttk.Button(left, text="Run Simulation", command=self.run_simulation)
        run_btn.pack(pady=8, fill="x")

        # Right: results panels
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        self.result_frames: dict[str, dict[str, ttk.Label]] = {}
        for sim_type in ("Surge", "Auction"):
            lf = ttk.LabelFrame(right, text=f"{sim_type} Simulation Results", padding=10)
            lf.pack(fill="x", pady=6)
            labels = {}
            for metric in ("Total Trips", "Total Social Surplus", "Total Revenue Surplus",
                           "Avg Social Surplus", "Avg Revenue Surplus"):
                row = ttk.Frame(lf)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=metric + ":", width=26, anchor="w").pack(side="left")
                val_lbl = ttk.Label(row, text="—", anchor="w")
                val_lbl.pack(side="left")
                labels[metric] = val_lbl
            self.result_frames[sim_type] = labels

        self.status_var = tk.StringVar(value="Adjust parameters and click Run.")
        ttk.Label(right, textvariable=self.status_var, foreground="gray").pack(pady=(8, 0))

    def _make_slider(self, parent, key, label, lo, hi, step, default):
        var = tk.DoubleVar(value=default)
        self.sliders[key] = var

        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        ttk.Label(row, text=label, width=26, anchor="w").pack(side="left")

        is_int = isinstance(step, int)
        fmt = "{:.0f}" if is_int else "{:.2f}"

        val_lbl = ttk.Label(row, text=fmt.format(default), width=6, anchor="e")
        val_lbl.pack(side="right")

        def on_change(v, _var=var, _lbl=val_lbl, _fmt=fmt, _step=step, _is_int=is_int):
            raw = float(v)
            snapped = round(round(raw / _step) * _step, 10)
            if _is_int:
                snapped = int(snapped)
            _lbl.config(text=_fmt.format(snapped))

        slider = ttk.Scale(row, from_=lo, to=hi, orient="horizontal",
                           variable=var, length=180, command=on_change)
        slider.pack(side="right", padx=4)

    def _get_val(self, key, is_int=False):
        v = self.sliders[key].get()
        return int(round(v)) if is_int else round(v, 10)

    def run_simulation(self):
        self.status_var.set("Running…")
        self.update_idletasks()

        try:
            params = Parameters(
                surge=SurgeParameters(
                    base_fare=self._get_val("base_fare"),
                    per_minute_rate=self._get_val("per_minute_rate"),
                    surge_multiplier=self._get_val("surge_multiplier"),
                ),
                auction=AuctionParameters(
                    reserve_price=self._get_val("reserve_price"),
                ),
                rider=RiderParameters(
                    init_valuation_mean=self._get_val("init_valuation_mean"),
                    init_valuation_std=self._get_val("init_valuation_std"),
                    dist_mean=self._get_val("dist_mean"),
                    dist_std=self._get_val("dist_std"),
                ),
                num_drivers=self._get_val("num_drivers", is_int=True),
                average_riders_per_minute=self._get_val("average_riders_per_minute"),
                time_steps=self._get_val("time_steps", is_int=True),
            )

            sim = Simulation(params=params)
            sim.run()

            ts = params.time_steps or 1

            results = {
                "Surge": sim.surge_simulation,
                "Auction": sim.auction_simulation,
            }

            for sim_type, s in results.items():
                labels = self.result_frames[sim_type]
                labels["Total Trips"].config(text=str(s.total_trips))
                labels["Total Social Surplus"].config(text=f"{s.social_surplus:.4f}")
                labels["Total Revenue Surplus"].config(text=f"{s.revenue_surplus:.4f}")
                labels["Avg Social Surplus"].config(text=f"{s.social_surplus / ts:.4f}")
                labels["Avg Revenue Surplus"].config(text=f"{s.revenue_surplus / ts:.4f}")

            self.status_var.set("Done.")
        except Exception as e:
            self.status_var.set(f"Error: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
