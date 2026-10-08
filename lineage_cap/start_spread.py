"""Shared elapsed clocks with a bounded distribution of inherited starts.

The start window has full span W, not standard deviation W. Each start group
inherits one clock; expansion decisions remain independent per suitable zone.
Our completion today and a common duration turn our start offset delta into
the earliest possible completion lead delta. No extra completion lottery.
"""

from dataclasses import dataclass
import math

import numpy as np

from .expansion import C_MPC_PER_GYR, galaxy_probability, quadrature
from .inference import HeadStartBound


def start_group_probability(completions, q, start_fraction, groups=1):
    """Average over shared starts BEFORE taking the galaxy event probability.

    H equal-sized independent ancestry groups: each has m/H zones and one
    common start. `per_zone` is the separate fully independent-start limit.
    """
    if groups == "per_zone":
        return galaxy_probability(completions, q * start_fraction)
    if not isinstance(groups, (int, float)) or not math.isfinite(groups) or groups < 1:
        raise ValueError("Require >=1 independent start groups or 'per_zone'")
    p_group = galaxy_probability(completions / groups, q)
    return galaxy_probability(groups, start_fraction * p_group)


def spread_expected_count(h, geometry, head_start, q, speed_c, kernel,
                          span_gyr, groups=1):
    """Expected externally visible galaxies, marginalized over uniform starts.

    The first frontier is now-delta; others lie in [now-delta, now-delta+W].
    A deadline t admits start fraction clip((t-now+delta)/W,0,1).
    At W=0 this reduces to the original synchronized inherited model.
    Splitting the radial integral at the CDF kink keeps thin tails resolved.
    """
    delta, q = np.broadcast_arrays(np.asarray(head_start, dtype=float), q)
    if np.any(~np.isfinite(delta)) or np.any(delta < 0) or np.any(delta > h.duration + 1e-12):
        raise ValueError("Head start must lie within the modeled history")
    if not math.isfinite(span_gyr) or span_gyr < 0:
        raise ValueError("Start span must be finite and nonnegative")
    if not math.isfinite(speed_c) or not 0 <= speed_c <= 1:
        raise ValueError("Require 0 <= speed/c <= 1")
    if np.any(~np.isfinite(q)) or np.any(q < 0) or np.any(q > 1):
        raise ValueError("Require 0 <= expansion probability <= 1")
    # Validate even when speed is zero.
    start_group_probability(np.zeros_like(delta), q, np.zeros_like(delta), groups)
    delay = geometry.delay(speed_c, kernel)
    propagation = C_MPC_PER_GYR * (speed_c if kernel.startswith("physical") else 1)
    if propagation == 0 or not math.isfinite(delay):
        return np.zeros_like(delta)
    available = np.maximum(delta - delay, 0)
    radius = propagation * available
    z0, w0 = quadrature(geometry.quadrature_order)
    if span_gyr == 0:
        z = np.broadcast_to(z0, delta.shape + z0.shape)
        weights = w0
        fraction = np.ones_like(z)
    else:
        with np.errstate(divide="ignore", invalid="ignore"):
            cut = np.where(available > 0, np.maximum(1 - span_gyr / available, 0), 0)
        z = np.concatenate((cut[..., None] * z0,
                            cut[..., None] + (1-cut[..., None]) * z0), axis=-1)
        weights = np.concatenate((cut[..., None] * w0,
                                  (1-cut[..., None]) * w0), axis=-1)
        fraction = np.clip(available[..., None] * (1-z) / span_gyr, 0, 1)
    deadline = h.now - delay - available[..., None] * z
    p = start_group_probability(h.zones(deadline), q[..., None], fraction, groups)
    return (4 * math.pi * geometry.galaxy_density * radius ** 3
            * np.sum(p * z ** 2 * weights, axis=-1))


@dataclass(frozen=True)
class SpreadBound:
    lead: HeadStartBound
    start_offset_max_gyr: np.ndarray
    percentile_max: np.ndarray
    first_one_in: np.ndarray
    constrained_within_window: np.ndarray


def spread_bound(h, geometry, q, speed_c, kernel, span_gyr, groups=1,
                 mu_threshold=2.995732273553991, tolerance=1e-9):
    """Invert the completion lead, then limit our start to its own window.

    A root beyond W permits every start percentile; it is NOT evidence that
    our start lies outside the distribution. W=0 has no start-percentile
    information, but retains the original completion-lead bound.
    """
    if mu_threshold <= 0 or tolerance <= 0:
        raise ValueError("Require positive threshold and tolerance")
    if span_gyr > h.duration:
        raise ValueError("The start window must fit within the modeled history")
    q = np.asarray(q, dtype=float)
    low, high = np.zeros_like(q), np.full_like(q, h.duration)
    maximum = spread_expected_count(h, geometry, high, q, speed_c, kernel, span_gyr, groups)
    constrained = maximum >= mu_threshold
    for _ in range(64):
        if np.max(high-low) <= tolerance:
            break
        mid = (low+high)/2
        mu = spread_expected_count(h, geometry, mid, q, speed_c, kernel, span_gyr, groups)
        high = np.where(mu >= mu_threshold, mid, high)
        low = np.where(mu >= mu_threshold, low, mid)
    delta = np.where(constrained, (low+high)/2, h.duration)
    if span_gyr == 0:
        unknown = np.full_like(delta, np.nan)
        return SpreadBound(HeadStartBound(delta, constrained), unknown, unknown,
                           unknown, np.zeros_like(constrained))
    offset = np.minimum(delta, span_gyr)
    percentile = offset / span_gyr
    return SpreadBound(HeadStartBound(delta, constrained), offset, percentile,
                       1 / percentile, constrained & (delta < span_gyr))


def spread_q_ceiling(h, geometry, start_percentile, span_gyr, speed_c, kernel,
                     groups=1, mu_threshold=2.995732273553991):
    """q ceiling for a specified location in a nonzero start window."""
    if not 0 <= start_percentile <= 1 or not 0 < span_gyr <= h.duration or mu_threshold <= 0:
        raise ValueError("Require percentile in [0,1], 0<W<=history and mu>0")
    delta = start_percentile * span_gyr
    args = (h, geometry, delta)
    if spread_expected_count(*args, 1, speed_c, kernel, span_gyr, groups) < mu_threshold:
        return 1.0, False
    low, high = -40.0, 0.0
    if spread_expected_count(*args, 10**low, speed_c, kernel, span_gyr, groups) > mu_threshold:
        raise ValueError("q ceiling below 1e-40; extend bracket")
    for _ in range(60):
        mid = (low+high)/2
        if spread_expected_count(*args, 10**mid, speed_c, kernel, span_gyr, groups) >= mu_threshold:
            high = mid
        else:
            low = mid
    return 10**((low+high)/2), True


def cosmic_age_at_redshift(z, h0_km_s_mpc=67.4, omega_m=.315, omega_r=9.2e-5,
                           quadrature_order=192):
    """Flat matter+radiation+Lambda age; used only for the epoch source check.

    This does not cosmologically correct the flat-space visibility model.
    """
    z = np.asarray(z, dtype=float)
    if np.any(z < 0) or h0_km_s_mpc <= 0 or min(omega_m, omega_r) < 0 or omega_m+omega_r > 1:
        raise ValueError("Invalid cosmology or redshift")
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    a_max = 1/(1+z)
    a = a_max[..., None] * (nodes+1)/2
    omega_lambda = 1-omega_m-omega_r
    # H0 / c[km/s] * c[Mpc/Gyr] converts H0 to 1/Gyr.
    hubble_gyr = h0_km_s_mpc / 299792.458 * C_MPC_PER_GYR
    integral = np.sum(weights * a / np.sqrt(omega_r + omega_m*a + omega_lambda*a**4), axis=-1)
    return a_max/2 * integral / hubble_gyr
