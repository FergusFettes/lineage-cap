"""Normal iid-duration tail estimate used in note.qmd Section 5.

One shared start for all galaxies; lineage durations are independent
normal draws.  For each duration spread sigma_T, this solves for the
mean duration that puts the external visibility count on
mu = -log(0.05), using the visibility integral in note Appendix A:

    F(t)   = Phi((t - S - m) / sigma_T)
    p_g(t) = 1 - [1 - q F(t)] ** N(t)
    mu     = 4 pi n_g int r^2 p_g[t0 - D/v - r/c] dr

Run from the repository root:

    uv run python -m lineage_cap.iid_tail

Output: results/iid_tail/normal_tail_estimate.csv
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np

from lineage_cap.expansion import C_MPC_PER_GYR, Geometry
from lineage_cap.history import History

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "configs/baseline.json").read_text())
OUT = ROOT / "results/iid_tail/normal_tail_estimate.csv"

NORM = NormalDist()
MU_STAR = -math.log(0.05)
SPEED_C = 0.5
Q = 1.0
SIGMAS_GYR = (0.03, 0.136, 0.408, 1.36)
REFERENCE_DURATION_GYR = 13.6

def expected_visible(sigma_gyr: float, z0: float, history: History, geometry: Geometry) -> float:
    """Visibility mu when Earth's duration sits z0 sigma below the mean.

    z0 = (mean completion date - t0) / sigma.  At lookback tau the
    finished share is Phi(-z0 - tau / sigma).
    """
    delay = geometry.delay(SPEED_C, "remote_visibility")
    t0 = history.now
    n_g = float(CONFIG["abundance"]["galaxy_density_mpc3"])

    # Trapezoid in u = tau / sigma.  Five sigma past t0 the normal tail is
    # below Phi(-11), negligible against the volume growth on this range.
    u_max = 5.0
    u = np.linspace(0.0, u_max, 4001)
    tau = u * sigma_gyr
    radius = C_MPC_PER_GYR * np.maximum(tau - delay, 0.0)
    finished = np.array([NORM.cdf(-z0 - x) for x in u])
    zones = history.zones(t0 - tau)
    # Stable 1 - (1 - qF)^N.
    p_gal = -np.expm1(zones * np.log1p(-Q * finished))
    integrand = radius**2 * p_gal * C_MPC_PER_GYR * sigma_gyr
    integral = np.trapezoid(integrand, u)
    return float(4 * math.pi * n_g * integral)


def solve_z(sigma_gyr: float, history: History, geometry: Geometry) -> float:
    lo, hi = 3.0, 10.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if expected_visible(sigma_gyr, mid, history, geometry) > MU_STAR:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

def expected_arrived(sigma_gyr: float, z0: float, delta_gyr: float, history: History) -> float:
    """Expected origin galaxies whose front has reached us by t0+delta.

    A galaxy at radius r must have emerged by t0+delta-r/v.  Integrate
    over emergence offset x (Gyr relative to t0), so r=v_c*(delta-x).
    """
    t0 = history.now
    n_g = float(CONFIG["abundance"]["galaxy_density_mpc3"])
    front_speed = SPEED_C * C_MPC_PER_GYR
    x_min = max(-5.0 * sigma_gyr, history.start - t0)
    x = np.linspace(x_min, delta_gyr, 4001)
    radius = front_speed * (delta_gyr - x)
    finished = np.array([NORM.cdf(xx / sigma_gyr - z0) for xx in x])
    zones = history.zones(t0 + x)
    p_gal = -np.expm1(zones * np.log1p(-Q * np.minimum(finished, 1.0 - 1e-15)))
    integral = np.trapezoid(radius**2 * p_gal * front_speed, x)
    return float(4 * math.pi * n_g * integral)


def median_first_arrival_myr(sigma_gyr: float, z0: float, history: History) -> tuple[float, float]:
    """Median wait for the first external front, given none by t0."""
    base = expected_arrived(sigma_gyr, z0, 0.0, history)
    lo, hi = 0.0, 2.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if expected_arrived(sigma_gyr, z0, mid, history) - base < math.log(2):
            lo = mid
        else:
            hi = mid
    return base, 500.0 * (lo + hi)


def main() -> None:
    history = History.from_config(CONFIG)
    geometry = Geometry.from_config(CONFIG)
    zones_today = float(history.zones(history.now))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "sigma_T_myr",
                "sigma_T_over_13.6gyr",
                "z0",
                "F_t0",
                "expected_mw_finishers_by_t0",
                "p_first_in_mw",
                "mean_completion_after_t0_myr",
                "mu_check",
                "expected_arrivals_by_t0",
                "median_first_arrival_after_t0_myr_conditional",
            ]
        )
        for sigma in SIGMAS_GYR:
            z0 = solve_z(sigma, history, geometry)
            f_t0 = NORM.cdf(-z0)
            expected_mw = Q * zones_today * f_t0
            arrived_by_t0, median_arrival_myr = median_first_arrival_myr(sigma, z0, history)
            row = [
                f"{sigma * 1000:.0f}",
                f"{sigma / REFERENCE_DURATION_GYR:.4f}",
                f"{z0:.4f}",
                f"{f_t0:.6e}",
                f"{expected_mw:.6e}",
                f"{math.exp(-expected_mw):.6f}",
                f"{z0 * sigma * 1000:.1f}",
                f"{expected_visible(sigma, z0, history, geometry):.6f}",
                f"{arrived_by_t0:.6f}",
                f"{median_arrival_myr:.1f}",
            ]
            writer.writerow(row)
            print(",".join(row))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
