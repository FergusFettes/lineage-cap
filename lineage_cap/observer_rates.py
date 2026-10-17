"""N sweep of the normal iid tail, and observer rates under full non-indexical conditioning.

Two tables for first-flush-likelihood.qmd Section 5 and Appendix A.

1. N sweep.  Rescale the trajectory history by a constant factor and
   re-solve the iid_tail visibility boundary.  Reports F(t0), the home
   count N F(t0), z0 and the exponent of F against N.

2. Observer rates.  Under full non-indexical conditioning the likelihood
   of "an observer emerges near t0 under an empty sky" is proportional,
   when small, to the expected rate of such emergences.  Per galaxy at
   t0, with every scenario held at the same visibility boundary:

   - process clock, iid normal durations, q = 1:  N(t0) f(t0)
   - process clock with a late filter: q at its sky ceiling for a mean
     completion placed z0 sigma after t0, N(t0) f(t0)
   - planet clock with the improbability before emergence (loud on
     emergence): Lambda_max / L
   - planet clock with the improbability after emergence (late filter,
     q at its ceiling): N0 / L
   - hard-steps lottery, loud on emergence: each planet emerges at age a
     with density n a^(n-1) / tau^n (rare-event limit), optionally only
     inside a habitable window of length W.  The rate 1/tau^n is solved
     for the sky boundary.

   Each rate is multiplied by the probability of no earlier loud lineage
   at home, exp(-expected), so the counted observers also see a quiet
   galaxy.  The external sky factor is 5% for every row and cancels.

   Lambda_max is the rare-expander planetary ceiling for the linear ramp,
   3 L mu* / (pi n_g c^3 (L - T - D/v)^4) at T = 4.6 Gyr.

Run from the repository root:

    uv run python -m lineage_cap.observer_rates

3. FNC peak.  At fixed sigma_T and q = 1, the FNC log-likelihood of the
   mean placement z0 is log f(t0) - mu_vis(z0) - N F(t0): observer rate,
   empty external sky, quiet home.  Unlike the empty sky alone it has an
   interior maximum.  Reports the maximising z0 next to the 5% boundary.

Outputs: results/iid_tail/n_sweep.csv, results/iid_tail/observer_rates.csv,
results/iid_tail/fnc_peak.csv
"""

from __future__ import annotations

import csv
import math

import numpy as np

from lineage_cap import iid_tail
from lineage_cap.expansion import C_MPC_PER_GYR, Geometry
from lineage_cap.history import History

N_SCALES = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)
SWEEP_SIGMAS_GYR = (0.03, 0.136, 0.408)
PLANET_T_GYR = 4.6
LATE_FILTER_Z0 = (3.0, 1.0, 0.0)
HARD_STEPS_N = (3, 6, 9)
HARD_STEPS_WINDOWS_GYR = (math.inf, 5.0)
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


def q_ceiling(sigma_gyr: float, z0: float, history: History, geometry: Geometry) -> float:
    """Largest q keeping the iid-tail sky on the boundary for fixed z0."""
    lo, hi = -40.0, 0.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if iid_tail.expected_visible(sigma_gyr, z0, history, geometry, q=10**mid) > iid_tail.MU_STAR:
            hi = mid
        else:
            lo = mid
    return 10**lo


class HardSteps:
    """Expected emergences per galaxy for an n-step lottery on the linear ramp.

    Planets are born at N0/L per Gyr from s.  A planet of age a emerges at
    rate k n a^(n-1) while a < window, with k = 1/tau^n.
    """

    def __init__(self, n: int, window_gyr: float, history: History):
        self.n = n
        self.window = window_gyr
        self.start = history.start
        self.birth_rate = float(history.zones(history.now)) / (history.now - history.start)

    def rate(self, time: np.ndarray, k: float) -> np.ndarray:
        age = np.clip(time - self.start, 0.0, self.window)
        return self.birth_rate * k * age**self.n

    def expected(self, time: np.ndarray, k: float) -> np.ndarray:
        x = np.maximum(time - self.start, 0.0)
        inside = np.minimum(x, self.window)
        expired = 0.0 if math.isinf(self.window) else self.window**self.n * np.maximum(x - self.window, 0.0)
        return self.birth_rate * k * (inside ** (self.n + 1) / (self.n + 1) + expired)


def hard_steps_boundary(model: HardSteps, history: History, geometry: Geometry) -> float:
    """k = 1/tau^n putting the visibility count on mu*."""
    n_g = float(iid_tail.CONFIG["abundance"]["galaxy_density_mpc3"])
    t_edge = history.now - geometry.delay(iid_tail.SPEED_C, "remote_visibility")
    span = t_edge - history.start
    breaks = sorted({0.0, span, min(max(span - model.window, 0.0), span)})
    nodes, weights = np.polynomial.legendre.leggauss(400)

    def mu(k: float) -> float:
        total = 0.0
        for a, b in zip(breaks[:-1], breaks[1:]):
            u = 0.5 * (b - a) * nodes + 0.5 * (a + b)
            p_gal = -np.expm1(-model.expected(t_edge - u, k))
            total += 0.5 * (b - a) * float(np.sum(weights * u**2 * p_gal))
        return 4 * math.pi * n_g * C_MPC_PER_GYR**3 * total

    lo, hi = -80.0, 10.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if mu(10**mid) > iid_tail.MU_STAR:
            hi = mid
        else:
            lo = mid
    return 10**lo


def fnc_log_likelihood(sigma_gyr: float, z0: float, n_now: float, history: History, geometry: Geometry) -> float:
    mu = iid_tail.expected_visible(sigma_gyr, z0, history, geometry)
    return -0.5 * z0 * z0 - math.log(sigma_gyr) - mu - n_now * iid_tail.NORM.cdf(-z0)


def fnc_peak(sigma_gyr: float, n_now: float, history: History, geometry: Geometry) -> float:
    """Golden-section maximum of the FNC log-likelihood over z0."""
    lo, hi = 3.0, 10.0
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        a, b = hi - ratio * (hi - lo), lo + ratio * (hi - lo)
        if fnc_log_likelihood(sigma_gyr, a, n_now, history, geometry) > fnc_log_likelihood(
            sigma_gyr, b, n_now, history, geometry
        ):
            hi = b
        else:
            lo = a
    return 0.5 * (lo + hi)


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
    sigma = 0.136
    for z0 in LATE_FILTER_Z0:
        q = q_ceiling(sigma, z0, history, geometry)
        f = iid_tail.NORM.cdf(-z0)
        density = math.exp(-0.5 * z0 * z0) / math.sqrt(2 * math.pi) / sigma
        rates.append(
            (f"process clock, sigma_T=136 Myr, late filter q={q:.2e}, mean {z0:g} sigma after t0",
             n_now * density, math.exp(-q * n_now * f))
        )
    t0 = np.array([history.now])
    for window in HARD_STEPS_WINDOWS_GYR:
        for n in HARD_STEPS_N:
            model = HardSteps(n, window, history)
            k = hard_steps_boundary(model, history, geometry)
            label = "no window" if math.isinf(window) else f"{window:g} Gyr window"
            rates.append(
                (f"hard steps n={n}, {label}, loud on emergence",
                 float(model.rate(t0, k)[0]), math.exp(-float(model.expected(t0, k)[0])))
            )
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

    with (OUT_DIR / "fnc_peak.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["sigma_T_myr", "z0_boundary", "z0_peak", "peak_minus_boundary_myr", "mu_vis_at_peak",
             "F_t0_at_peak", "N_F_t0_at_peak", "mean_completion_after_t0_myr_at_peak", "log_likelihood_gain",
             "median_first_arrival_myr_given_empty_sky_at_peak"]
        )
        for sigma in SWEEP_SIGMAS_GYR:
            zb = iid_tail.solve_z(sigma, history, geometry)
            zp = fnc_peak(sigma, n_now, history, geometry)
            f = iid_tail.NORM.cdf(-zp)
            gain = fnc_log_likelihood(sigma, zp, n_now, history, geometry) - fnc_log_likelihood(
                sigma, zb, n_now, history, geometry
            )
            row = [f"{sigma * 1000:.0f}", f"{zb:.4f}", f"{zp:.4f}", f"{(zp - zb) * sigma * 1000:.1f}",
                   f"{iid_tail.expected_visible(sigma, zp, history, geometry):.4f}", f"{f:.6e}",
                   f"{n_now * f:.6e}", f"{zp * sigma * 1000:.1f}", f"{gain:.4f}",
                   f"{iid_tail.median_first_arrival_myr(sigma, zp, history, geometry)[2]:.1f}"]
            writer.writerow(row)
            print(",".join(row))


if __name__ == "__main__":
    main()
