"""Independent arithmetic for the 16 October 2026 critical review.

Run from the repository root:
    PYTHONPATH=. uv run python notes/critical-review-2026-10-16/calculations.py

Prints JSON; does not modify the paper or its production results. Uses a
separate erfc CDF and Gauss-Legendre integration, compared with iid_tail's
trapezoidal implementation. Units: Gyr, Mpc, dimensionless counts.
"""

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np

from lineage_cap import iid_tail
from lineage_cap.expansion import Geometry
from lineage_cap.history import History


ROOT = Path(__file__).resolve().parents[2]
CONFIG_BYTES = (ROOT / "configs/baseline.json").read_bytes()
CONFIG = json.loads(CONFIG_BYTES)
NOW = CONFIG["time"]["now_gyr"]
START = CONFIG["time"]["ramp_start_gyr"]
LENGTH = NOW - START
N0 = (CONFIG["abundance"]["stars_now"]
      * CONFIG["abundance"]["appropriate_fraction"]
      * CONFIG["abundance"]["trajectories_per_appropriate_zone"])
ALPHA = CONFIG["history"]["count_exponent"]
NG = CONFIG["abundance"]["galaxy_density_mpc3"]
C = 299792458 * (365.25 * 86400 * 1e9) / (
    648000 / math.pi * 149597870700 * 1e6)
V = 0.5 * C
DELAY = CONFIG["expansion"]["host_galaxy_diameter_kpc"] / 1000 / V
TARGET = -math.log(0.05)
# These are the published iid-tail scenarios, with q=1 and zero launch lag.
SIGMAS = (0.03, 0.136, 0.408, 1.36)
assert CONFIG["expansion"]["launch_delay_gyr"] == 0


@lru_cache(None)
def nodes(order):
    return np.polynomial.legendre.leggauss(order)


def integrate(function, lower, upper, order=256):
    if upper <= lower:
        return 0.0
    x, weights = nodes(order)
    argument = lower + (upper - lower) * (x + 1) / 2
    return float((upper - lower) / 2 * np.dot(weights, function(argument)))


def galaxy_cdf(offset, sigma, z):
    """CDF of first loud crossing, at cosmic date NOW + offset, q=1."""
    offsets = np.asarray(offset)
    fraction = np.array([
        0.5 * math.erfc((z - x / sigma) / math.sqrt(2))
        for x in offsets.flat
    ]).reshape(offsets.shape)
    count = N0 * np.clip((NOW + offsets - START) / LENGTH, 0, 1)**ALPHA
    # The cap only affects large positive offsets, outside the review roots.
    fraction = np.minimum(fraction, 1 - 1e-15)
    return -np.expm1(count * np.log1p(-fraction))


def expected_count(sigma, z, wait=0.0, kernel="visible", order=256):
    speed = C if kernel == "visible" else V
    delay = DELAY if kernel == "visible" else 0.0
    # Earlier than ten sigma before today contributes negligibly at these z.
    upper = min(LENGTH + wait - delay, 10 * sigma + wait - delay)
    integral = integrate(
        lambda tau: tau**2 * galaxy_cdf(wait - delay - tau, sigma, z),
        0, upper, order,
    )
    return 4 * math.pi * NG * speed**3 * integral


def increasing_root(function, target, lower, upper):
    assert function(lower) <= target <= function(upper)
    for _ in range(60):
        midpoint = (lower + upper) / 2
        if function(midpoint) < target:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def new_arrivals_given_empty_sky(sigma, z, wait, order=256):
    """Intensity of A_future minus (V_now union A_now), not two marginals.

    Each Poisson galaxy has a first-crossing mark with CDF galaxy_cdf.
    Conditioning on no marks in V_now union A_now leaves a Poisson process
    on its complement. This conditions only on the modeled observations;
    it is not a full anthropic likelihood or a catalog-conditioned model.
    """
    change = DELAY / (1 / V - 1 / C)
    radius_max = (wait + DELAY) / (1 / V - 1 / C)

    def integrand(radius):
        arrival_deadline = wait - radius / V
        excluded_deadline = np.maximum(-DELAY - radius / C, -radius / V)
        probability = galaxy_cdf(arrival_deadline, sigma, z)
        probability -= galaxy_cdf(excluded_deadline, sigma, z)
        return radius**2 * np.maximum(probability, 0)

    # Split at the deadline crossover and at the post-today N(t) cap.
    breaks = sorted({0, min(change, radius_max), min(V * wait, radius_max), radius_max})
    return 4 * math.pi * NG * sum(
        integrate(integrand, a, b, order) for a, b in zip(breaks, breaks[1:])
    )


class Python312CDF:
    """Exact formula used by CPython 3.12 statistics.NormalDist.cdf.

    https://github.com/python/cpython/blob/3.12/Lib/statistics.py
    Used to isolate cancellation in a permitted older runtime; not an
    assertion that a full Python 3.12 dependency environment was run here.
    """

    @staticmethod
    def cdf(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def main():
    history = History.from_config(CONFIG)
    geometry = Geometry.from_config(CONFIG)
    rows = []
    portability = []
    for sigma in SIGMAS:
        z = increasing_root(lambda x: -expected_count(sigma, x), -TARGET, 3, 10)
        production_z = iid_tail.solve_z(sigma, history, geometry)
        arrival_now = expected_count(sigma, z, kernel="arrival")
        arrival_only = increasing_root(
            lambda wait: expected_count(sigma, z, wait, "arrival") - arrival_now,
            math.log(2), 0, 2,
        )
        both = increasing_root(
            lambda wait: new_arrivals_given_empty_sky(sigma, z, wait),
            math.log(2), 0, 2,
        )
        fraction = 0.5 * math.erfc(z / math.sqrt(2))
        visible_error = abs(expected_count(sigma, z, order=512) / TARGET - 1)
        conditional_error = abs(
            new_arrivals_given_empty_sky(sigma, z, both, order=512) / math.log(2) - 1)
        assert visible_error < 1e-8
        assert conditional_error < 1e-8
        assert both > arrival_only
        rows.append({
            "sigma_myr": sigma * 1000,
            "z": z,
            "production_z": production_z,
            "F_today": fraction,
            "home_mean": N0 * fraction,
            "home_none_probability": math.exp(-N0 * fraction),
            "mean_completion_after_today_myr": z * sigma * 1000,
            "arrival_intensity_today": arrival_now,
            "median_given_no_arrival_myr": arrival_only * 1000,
            "median_given_empty_sky_and_no_arrival_myr": both * 1000,
            "visible_256_to_512_relative_error": visible_error,
            "conditional_256_to_512_relative_error": conditional_error,
            "external_empty_and_home_none_probability": 0.05 * math.exp(-N0 * fraction),
        })
        current_cdf = iid_tail.NORM
        try:
            iid_tail.NORM = Python312CDF()
            old_z = iid_tail.solve_z(sigma, history, geometry)
        finally:
            iid_tail.NORM = current_cdf
        portability.append({
            "sigma_myr": sigma * 1000,
            "z_with_python312_cdf": old_z,
            "true_mu_at_that_z": expected_count(sigma, old_z),
            "relative_boundary_error": expected_count(sigma, old_z) / TARGET - 1,
        })

    shifted = []
    sigma, z = 0.136, rows[1]["z"]
    for shift in (0, 1, 2, 5):
        both = increasing_root(
            lambda wait: new_arrivals_given_empty_sky(sigma, z + shift, wait),
            math.log(2), 0, 3,
        )
        shifted.append({
            "mean_shift_in_sigma": shift,
            "external_empty_probability": math.exp(-expected_count(sigma, z + shift)),
            "median_given_empty_sky_and_no_arrival_myr": both * 1000,
        })

    planetary = []
    for start in (0.2, 1, 2, 4):
        length = NOW - start
        ceiling = 3 * length * TARGET / (
            math.pi * NG * C**3 * (length - 4.6 - DELAY)**4)
        planetary.append({"history_start_gyr": start, "rare_limit_lambda_ceiling": ceiling})

    windows = [{
        "width_myr": width * 1000,
        "lead_myr": 1000 * (DELAY + (3 * width * TARGET / (math.pi * NG * C**3))**0.25),
    } for width in (0.1, 0.2, 0.5, 5)]

    print(json.dumps({
        "scope": "independent review; same ideal q=1, v=0.5c, flat Poisson scenario",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "config_sha256": hashlib.sha256(CONFIG_BYTES).hexdigest(),
        "normal_tail": rows,
        "later_mean_examples": shifted,
        "python312_cdf_emulation": portability,
        "planet_history_sensitivity": planetary,
        "saturated_start_windows": windows,
        "saturated_visibility_lead_myr": 1000 * (
            DELAY + (3 * TARGET / (4 * math.pi * NG * C**3))**(1/3)),
        "illustrative_m31_lead_myr_at_0_78_mpc": 1000 * (DELAY + 0.78 / C),
    }, indent=2))


if __name__ == "__main__":
    main()
