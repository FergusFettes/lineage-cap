"""N sweep of the normal iid tail, and observer rates under full non-indexical conditioning.

Two tables for head-start-cap.qmd Section 5 and Appendix A.

1. N sweep.  Rescale the trajectory history by a constant factor and
   re-solve the iid_tail visibility boundary.  Reports F(t0), the home
   count N F(t0), z0 and the exponent of F against N.

2. Observer rates.  Under full non-indexical conditioning the likelihood
   of "an observer emerges near t0 under an empty sky" is proportional,
   when small, to the expected rate of such emergences.  Per galaxy at
   t0, with every scenario held at the same visibility boundary:

   - process clock, iid normal durations, q = 1:  N(t0) f(t0)
   - planet clock with the improbability before emergence (hard-steps
     proxy, loud on emergence): Lambda_max / L
   - planet clock with the improbability after emergence (late filter,
     q at its ceiling): N0 / L

   Each rate is multiplied by the probability of no earlier loud lineage
   at home, exp(-expected), so the counted observers also see a quiet
   galaxy.  The external sky factor is 5% for every row and cancels.

   Lambda_max is the rare-expander planetary ceiling for the linear ramp,
   3 L mu* / (pi n_g c^3 (L - T - D/v)^4) at T = 4.6 Gyr.

Run from the repository root:

    uv run python -m lineage_cap.observer_rates

Outputs: results/iid_tail/n_sweep.csv, results/iid_tail/observer_rates.csv
"""

from __future__ import annotations

import csv
import math

from lineage_cap import iid_tail
from lineage_cap.expansion import C_MPC_PER_GYR, Geometry
from lineage_cap.history import History

N_SCALES = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)
SWEEP_SIGMAS_GYR = (0.03, 0.136, 0.408)
PLANET_T_GYR = 4.6
OUT_DIR = iid_tail.ROOT / "results/iid_tail"


class ScaledHistory:
    """A History with every trajectory count multiplied by `scale`."""

    def __init__(self, history: History, scale: float):
        self.history = history
        self.scale = scale
        self.now = history.now
        self.start = history.start

    def zones(self, time):
        return self.scale * self.history.zones(time)


def planetary_ceiling(history: History, geometry: Geometry) -> float:
    span = history.now - history.start
    lead = span - PLANET_T_GYR - geometry.delay(iid_tail.SPEED_C, "remote_visibility")
    n_g = float(iid_tail.CONFIG["abundance"]["galaxy_density_mpc3"])
    return 3 * span * iid_tail.MU_STAR / (math.pi * n_g * C_MPC_PER_GYR**3 * lead**4)


def main() -> None:
    history = History.from_config(iid_tail.CONFIG)
    geometry = Geometry.from_config(iid_tail.CONFIG)
    n_now = float(history.zones(history.now))

    with (OUT_DIR / "n_sweep.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sigma_T_myr", "N_t0", "z0", "F_t0", "N_F_t0", "exponent_vs_N"])
        for sigma in SWEEP_SIGMAS_GYR:
            rows = []
            for scale in N_SCALES:
                z0 = iid_tail.solve_z(sigma, ScaledHistory(history, scale), geometry)
                rows.append((scale * n_now, z0, iid_tail.NORM.cdf(-z0)))
            exponent = -math.log(rows[-1][2] / rows[0][2]) / math.log(rows[-1][0] / rows[0][0])
            for n, z0, f in rows:
                row = [f"{sigma * 1000:.0f}", f"{n:.0e}", f"{z0:.4f}", f"{f:.6e}", f"{n * f:.6e}", f"{exponent:.4f}"]
                writer.writerow(row)
                print(",".join(row))

    span = history.now - history.start
    ceiling = planetary_ceiling(history, geometry)
    rates = []
    for sigma in SWEEP_SIGMAS_GYR:
        z0 = iid_tail.solve_z(sigma, history, geometry)
        density = math.exp(-0.5 * z0 * z0) / math.sqrt(2 * math.pi) / sigma
        home = math.exp(-n_now * iid_tail.NORM.cdf(-z0))
        rates.append((f"process clock, sigma_T={sigma * 1000:.0f} Myr, q=1", n_now * density, home))
    crossed = 1 - PLANET_T_GYR / span
    rates.append(("planet clock, improbability before emergence", ceiling / span, math.exp(-ceiling * crossed)))
    rates.append(("planet clock, late filter at q ceiling", n_now / span, math.exp(-ceiling * crossed)))
    reference = rates[1][1] * rates[1][2]

    with (OUT_DIR / "observer_rates.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["scenario", "emergences_per_galaxy_per_gyr_at_t0", "p_quiet_home", "ratio_to_process_136myr"]
        )
        for name, rate, home in rates:
            row = [name, f"{rate:.6e}", f"{home:.6f}", f"{rate * home / reference:.6e}"]
            writer.writerow(row)
            print(",".join(row))
    print(f"planetary ceiling Lambda_max = {ceiling:.6e}")


if __name__ == "__main__":
    main()
