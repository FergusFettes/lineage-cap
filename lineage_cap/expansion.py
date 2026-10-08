"""Flat-space observable volumes, with saturating probabilities per galaxy.

The primary visibility model is ideal detection of persistently loud galaxies.
Physical arrival is a separate diagnostic, not an additional independent datum.
"""

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np

from .clocks import completed_zones
from .history import History

# Exact SI c, Julian Gyr, and IAU parsec definition, converted to Mpc/Gyr.
C_MPC_PER_GYR = 299792458 * (365.25 * 86400 * 1e9) / (
    648000 / math.pi * 149597870700 * 1e6)
KERNELS = ("remote_visibility", "physical_arrival_diagnostic")


@dataclass(frozen=True)
class Geometry:
    galaxy_density: float = .01
    host_diameter_mpc: float = .03
    launch_delay_gyr: float = 0.0
    quadrature_order: int = 96

    def __post_init__(self):
        if any(not math.isfinite(x) or x < 0 for x in
               (self.galaxy_density, self.host_diameter_mpc, self.launch_delay_gyr)):
            raise ValueError("Geometry scales must be finite and nonnegative")
        if self.quadrature_order < 8:
            raise ValueError("Use at least 8 quadrature nodes")

    @classmethod
    def from_config(cls, config):
        return cls(config["abundance"]["galaxy_density_mpc3"],
                   config["expansion"]["host_galaxy_diameter_kpc"] / 1000,
                   config["expansion"]["launch_delay_gyr"],
                   config["inference"].get("quadrature_order", 96))

    def delay(self, speed_c, kernel):
        if kernel not in KERNELS:
            raise ValueError(f"Unknown observation kernel: {kernel}")
        if kernel == "physical_arrival_diagnostic":
            return self.launch_delay_gyr
        if speed_c == 0:
            return math.inf if self.host_diameter_mpc > 0 else self.launch_delay_gyr
        return self.launch_delay_gyr + self.host_diameter_mpc / (speed_c * C_MPC_PER_GYR)


@lru_cache(maxsize=8)
def quadrature(order):
    z, w = np.polynomial.legendre.leggauss(order)
    return (z + 1) / 2, w / 2


def galaxy_probability(completions, q):
    """Probability of >=1 expander; stable for tiny q and many completions."""
    m, q = np.broadcast_arrays(np.asarray(completions, dtype=float), q)
    if np.any(m < 0) or np.any(q < 0) or np.any(q > 1):
        raise ValueError("Require m >= 0 and 0 <= q <= 1")
    exponent = np.zeros_like(m)
    with np.errstate(divide="ignore"):
        np.multiply(m, np.log1p(-q), out=exponent, where=m > 0)
    return -np.expm1(exponent)


def expected_count(h: History, geometry: Geometry, head_start, q, speed_c,
                   mode, kind, kernel):
    """Expected observable external galaxies for a trial earliest-completion lead.

    Positions are a homogeneous Poisson process. At each radius, eligible zone
    completions give a galaxy-level probability, avoiding q*N > 1. Every cohort
    enters once through the cumulative count, not once per timestep.
    Arrays of trial head starts and q values are evaluated together.
    """
    delta, q = np.broadcast_arrays(np.asarray(head_start, dtype=float), q)
    if np.any(delta < 0) or np.any(delta > h.duration + 1e-12):
        raise ValueError("Head start must lie within the modeled history")
    if not 0 <= speed_c <= 1:
        raise ValueError("Require 0 <= speed/c <= 1")
    if np.any(q < 0) or np.any(q > 1):
        raise ValueError("Require 0 <= expansion probability <= 1")
    delay = geometry.delay(speed_c, kernel)
    propagation = C_MPC_PER_GYR * (
        speed_c if kernel == "physical_arrival_diagnostic" else 1)
    if propagation == 0 or not math.isfinite(delay):
        return np.zeros_like(delta)
    available = np.maximum(delta - delay, 0)
    radius = propagation * available
    z, weights = quadrature(geometry.quadrature_order)
    deadline = h.now - delay - available[..., None] * z
    frontier = (h.now - delta)[..., None]
    completions = completed_zones(h, deadline, frontier, mode, kind)
    p = galaxy_probability(completions, q[..., None])
    radial_integral = np.sum(p * z ** 2 * weights, axis=-1)
    return 4 * math.pi * geometry.galaxy_density * radius ** 3 * radial_integral
