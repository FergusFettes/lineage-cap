"""Invert conditional empty-sky likelihoods; frontier gaps are outputs."""

from dataclasses import dataclass

import numpy as np

from .clocks import required_threshold
from .expansion import Geometry, expected_count
from .history import History


@dataclass(frozen=True)
class HeadStartBound:
    delta_max: np.ndarray
    constrained: np.ndarray


def head_start_bound(h: History, geometry: Geometry, q, speed_c, mode, kind,
                     kernel, mu_threshold=2.995732273553991, tolerance=1e-9):
    """Largest lead with exp(-mu) >= the chosen empty-probability threshold.

    A capped value at the history duration is accompanied by constrained=False;
    it means this scenario supplies no bound within the modeled history.
    """
    if mu_threshold <= 0 or tolerance <= 0:
        raise ValueError("Require a positive threshold and tolerance")
    q = np.asarray(q, dtype=float)
    low, high = np.zeros_like(q), np.full_like(q, h.duration)
    at_max = expected_count(h, geometry, high, q, speed_c, mode, kind, kernel)
    constrained = at_max >= mu_threshold
    for _ in range(64):
        if np.max(high - low) <= tolerance:
            break
        mid = (low + high) / 2
        mu = expected_count(h, geometry, mid, q, speed_c, mode, kind, kernel)
        too_many = mu >= mu_threshold
        high = np.where(too_many, mid, high)
        low = np.where(too_many, low, mid)
    delta = np.where(constrained, (low + high) / 2, h.duration)
    return HeadStartBound(delta, constrained)


def earth_case_frontier(h, earth_age, kind):
    """Slowest process supported by a terrestrial history; faster is more visible."""
    if kind == "elapsed_time":
        return h.start + earth_age
    budget = h.exposure(h.now - earth_age, h.now)
    return float(h.time_for_capacity(budget))


def expansion_probability_ceiling(h, geometry, frontier, speed_c, mode, kind,
                                  kernel, mu_threshold=2.995732273553991):
    """Largest q permitting a specified clock; solve logarithmically for tiny q."""
    delta = h.now - frontier
    if expected_count(h, geometry, delta, 1.0, speed_c, mode, kind, kernel) < mu_threshold:
        return 1.0, False
    low, high = -40.0, 0.0
    if expected_count(h, geometry, delta, 10 ** low, speed_c, mode, kind, kernel) > mu_threshold:
        raise ValueError("q ceiling below 1e-40; extend the logarithmic bracket")
    for _ in range(60):
        mid = (low + high) / 2
        if expected_count(h, geometry, delta, 10 ** mid, speed_c, mode, kind, kernel) >= mu_threshold:
            high = mid
        else:
            low = mid
    return 10 ** ((low + high) / 2), True


def threshold_bounds(h, bound, kind):
    return required_threshold(h, h.now - bound.delta_max, kind)
