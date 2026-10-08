"""Independent analytic limits, cohort conservation and likelihood inversion."""

from dataclasses import replace
import math

import numpy as np
import pytest

from lineage_cap.clocks import completed_zones, completion_time, required_threshold
from lineage_cap.expansion import (
    C_MPC_PER_GYR, Geometry, expected_count, galaxy_probability,
)
from lineage_cap.history import History
from lineage_cap.inference import (
    earth_case_frontier, expansion_probability_ceiling, head_start_bound,
)


@pytest.mark.parametrize("mode", ["planet_linked", "inherited"])
@pytest.mark.parametrize("kind", ["elapsed_time", "integrated_capacity"])
def test_completions_match_independent_birth_cohort_count(mode, kind):
    h = History()
    frontier = 5.0
    births, numbers = h.cohorts(100000)
    times = completion_time(h, births, frontier, mode, kind)
    for deadline in [4.9, 5.0, 5.3, 9.2, 13.8]:
        actual = completed_zones(h, deadline, frontier, mode, kind)
        explicit = numbers[times <= deadline].sum()
        assert actual == pytest.approx(explicit, abs=h.zones_now / 100000)
    assert np.all(times >= births)


def test_capacity_inverse_roundtrip_including_future():
    h = History(beta=1.7)
    times = np.array([h.start, 1, 9.2, h.now, 17])
    assert h.time_for_capacity(h.capacity_time(times)) == pytest.approx(times)


def test_per_galaxy_probability_saturates_and_retains_tiny_q():
    assert galaxy_probability([0, 1, 1e10], 1) == pytest.approx([0, 1, 1])
    assert galaxy_probability([0, 1, 1e10], 0) == pytest.approx([0, 0, 0])
    assert galaxy_probability(1e10, 1e-24) == pytest.approx(1e-14, rel=1e-12)
    assert galaxy_probability(1e10, 1e-2) == 1


@pytest.mark.parametrize("kernel", ["remote_visibility", "physical_arrival_diagnostic"])
def test_saturated_inherited_model_matches_exact_sphere(kernel):
    h, g, speed, delta = History(), Geometry(), .5, 1.0
    propagation = C_MPC_PER_GYR * (speed if kernel.startswith("physical") else 1)
    radius = propagation * (delta - g.delay(speed, kernel))
    analytic = g.galaxy_density * 4 * math.pi / 3 * radius ** 3
    actual = expected_count(h, g, delta, 1, speed, "inherited", "elapsed_time", kernel)
    assert actual == pytest.approx(analytic, rel=1e-12)


@pytest.mark.parametrize("kernel", ["remote_visibility", "physical_arrival_diagnostic"])
def test_rare_expander_planetary_model_matches_analytic_integral(kernel):
    h, g, speed, delta, q = History(), Geometry(), .5, 9.0, 1e-18
    propagation = C_MPC_PER_GYR * (speed if kernel.startswith("physical") else 1)
    available = delta - g.delay(speed, kernel)
    # Independent small-q integral: integral_0^D r^2 (D-r) dr = D^4 / 12.
    analytic = (math.pi / 3 * g.galaxy_density * propagation ** 3
                * q * h.zones_now * available ** 4 / h.duration)
    actual = expected_count(h, g, delta, q, speed, "planet_linked", "elapsed_time", kernel)
    assert actual == pytest.approx(analytic, rel=1e-7)


def test_contact_speed_cube_scaling_and_zero_speed_limit():
    h, g = History(), Geometry()
    args = ("planet_linked", "integrated_capacity", "physical_arrival_diagnostic")
    slow = expected_count(h, g, 1, 1e-10, .1, *args)
    fast = expected_count(h, g, 1, 1e-10, .5, *args)
    assert fast / slow == pytest.approx(125)
    assert expected_count(h, g, 1, 1, 0, *args) == 0
    assert expected_count(h, g, 1, 1, 0, "inherited", "elapsed_time", "remote_visibility") == 0


@pytest.mark.parametrize("kind", ["elapsed_time", "integrated_capacity"])
def test_head_start_inverse_hits_forward_likelihood_boundary(kind):
    h, g = History(), Geometry()
    q = np.array([0, 1e-24, 1e-12, 1e-6, 1])
    bound = head_start_bound(h, g, q, .5, "planet_linked", kind, "remote_visibility")
    assert not np.any(bound.constrained[:2])
    assert np.all(bound.delta_max[:2] == h.duration)
    mu = expected_count(h, g, bound.delta_max[2:], q[2:], .5,
                        "planet_linked", kind, "remote_visibility")
    assert mu == pytest.approx(np.full(3, -math.log(.05)), rel=2e-6)
    assert np.all(np.diff(bound.delta_max) <= 0)


def test_expansion_ceiling_brackets_earth_case_and_matches_rare_limit():
    h, g, speed = History(), Geometry(), .5
    frontier = earth_case_frontier(h, 4.6, "elapsed_time")
    q, constrained = expansion_probability_ceiling(
        h, g, frontier, speed, "planet_linked", "elapsed_time", "remote_visibility")
    available = h.now - frontier - g.delay(speed, "remote_visibility")
    coefficient = math.pi / 3 * g.galaxy_density * C_MPC_PER_GYR ** 3 * h.zones_now * available ** 4 / h.duration
    assert constrained
    assert q == pytest.approx(-math.log(.05) / coefficient, rel=1e-7)
    mu = expected_count(h, g, h.now - frontier, q, speed,
                        "planet_linked", "elapsed_time", "remote_visibility")
    assert mu == pytest.approx(-math.log(.05), rel=1e-10)


def test_capacity_earth_case_uses_observed_local_exposure():
    h = History()
    frontier = earth_case_frontier(h, 4.6, "integrated_capacity")
    assert required_threshold(h, frontier, "integrated_capacity") == pytest.approx(
        h.exposure(h.now - 4.6, h.now))


def test_capacity_clock_quadrature_convergence():
    h, g = History(), Geometry()
    args = (.1, 1e-10, .5, "planet_linked", "integrated_capacity", "remote_visibility")
    normal = expected_count(h, g, *args)
    fine = expected_count(h, replace(g, quadrature_order=192), *args)
    assert normal == pytest.approx(fine, rel=5e-6)
