"""Independent integrals and limits of the distributed-start model."""

from dataclasses import replace
import math

import numpy as np
import pytest

from lineage_cap.expansion import C_MPC_PER_GYR, Geometry, expected_count, galaxy_probability
from lineage_cap.history import History
from lineage_cap.inference import head_start_bound
from lineage_cap.start_spread import (
    cosmic_age_at_redshift, spread_bound, spread_expected_count, spread_q_ceiling,
    start_group_probability,
)


@pytest.mark.parametrize("kernel", ["remote_visibility", "physical_arrival_diagnostic"])
def test_zero_spread_recovers_original_inherited_model(kernel):
    h, g = History(), Geometry()
    q, delta = np.array([0, 1e-18, 1e-10, 1]), np.array([.1, 9, .013, .013])
    assert spread_expected_count(h, g, delta, q, .5, kernel, 0) == pytest.approx(
        expected_count(h, g, delta, q, .5, "inherited", "elapsed_time", kernel), rel=1e-12)
    original = head_start_bound(h, g, q, .5, "inherited", "elapsed_time", kernel)
    new = spread_bound(h, g, q, .5, kernel, 0)
    assert new.lead.delta_max == pytest.approx(original.delta_max, rel=1e-12)
    assert np.all(np.isnan(new.percentile_max))


@pytest.mark.parametrize("delta,span", [(.05, .1), (.1, .1), (.2, .1), (.1, .00001)])
@pytest.mark.parametrize("kernel", ["remote_visibility", "physical_arrival_diagnostic"])
def test_uniform_shared_start_matches_exact_convolved_spheres(delta, span, kernel):
    h, g, speed, q = History(alpha=0), Geometry(), .5, 1e-12
    d = delta - g.delay(speed, kernel)
    propagation = C_MPC_PER_GYR * (speed if kernel.startswith("physical") else 1)
    # Average volumes of radii c*(D-u) over uniform u in [0,W].
    if d <= span:
        integral = d**4 / (12*span)
    else:
        integral = d**3/3-d**2*span/2+d*span**2/3-span**3/12
    analytic = 4*math.pi*g.galaxy_density*propagation**3 * integral * galaxy_probability(h.zones_now, q)
    assert spread_expected_count(h, g, delta, q, speed, kernel, span) == pytest.approx(analytic, rel=1e-11)


def test_shared_start_correlation_is_not_averaged_zone_count():
    assert start_group_probability(np.array(100.), 1, .1, 1) == pytest.approx(.1)
    assert start_group_probability(np.array(100.), 1, .1, 10) == pytest.approx(1-.9**10)
    assert start_group_probability(np.array(100.), 1, .1, "per_zone") == pytest.approx(1-.9**100)
    rare = [start_group_probability(np.array(1e10), 1e-20, .2, h) for h in (1, 100, "per_zone")]
    assert rare == pytest.approx([2e-11]*3, rel=1e-9)


def test_percentile_inverse_and_full_window_flags():
    h, g = History(), Geometry()
    bound = spread_bound(h, g, np.array([0, 1e-18, 1]), .5, "remote_visibility", .2)
    assert bound.percentile_max[:2] == pytest.approx([1, 1])
    assert not np.any(bound.constrained_within_window[:2])
    assert bound.constrained_within_window[2]
    assert bound.first_one_in[2] == pytest.approx(1/bound.percentile_max[2])
    assert spread_expected_count(h, g, bound.lead.delta_max[2], 1, .5,
                                 "remote_visibility", .2) == pytest.approx(-math.log(.05), rel=2e-7)


def test_percentile_q_ceiling_is_per_zone_and_matches_forward_count():
    h, g = History(), Geometry()
    q, constrained = spread_q_ceiling(h, g, .5, 2, .5, "remote_visibility")
    assert constrained and q < 1e-14
    assert spread_expected_count(h, g, 1, q, .5, "remote_visibility", 2) == pytest.approx(-math.log(.05), rel=1e-10)


def test_progenitor_group_outer_tail_converges():
    h, g = History(), Geometry()
    args = (.014, 1, .5, "remote_visibility", .5, "per_zone")
    assert spread_expected_count(h, g, *args) == pytest.approx(
        spread_expected_count(h, replace(g, quadrature_order=192), *args), rel=1e-7)


def test_disabled_expansion_and_invalid_inputs():
    h, g = History(), Geometry()
    for kernel in ("remote_visibility", "physical_arrival_diagnostic"):
        assert spread_expected_count(h, g, .1, 1, 0, kernel, .2) == 0
        assert spread_expected_count(h, g, .1, 0, .5, kernel, .2) == 0
    with pytest.raises(ValueError):
        spread_bound(h, g, 1, .5, "remote_visibility", 20)
    with pytest.raises(ValueError):
        spread_expected_count(h, g, .1, 1, .5, "remote_visibility", .2, 0)


def test_epoch_relabeling_changes_duration_not_the_completion_likelihood():
    h, g = History(), Geometry()
    delta = .03
    duration_at_early_start = h.now-.2-delta
    duration_at_late_start = h.now-4.1-delta
    assert duration_at_early_start-duration_at_late_start == pytest.approx(3.9)
    # With the same Goldilocks history the early frontier is the same date.
    assert (.2+duration_at_early_start) == pytest.approx(4.1+duration_at_late_start)
    shifted_ramp = replace(h, start=4.1)
    old = spread_expected_count(h, g, delta, 1e-10, .5, "remote_visibility", .2)
    new = spread_expected_count(shifted_ramp, g, delta, 1e-10, .5, "remote_visibility", .2)
    assert new != old
    assert abs(new/old-1) < .002


def test_cosmic_age_against_exact_matter_only_solution():
    z = np.array([15, 30])
    hubble_gyr = 67.4/299792.458*C_MPC_PER_GYR
    analytic = 2/(3*hubble_gyr)*(1+z)**(-1.5)
    assert cosmic_age_at_redshift(z, omega_m=1, omega_r=0, quadrature_order=384) == pytest.approx(analytic, rel=1e-8)
    checked = cosmic_age_at_redshift(z)
    assert .26 < checked[0] < .28 and .09 < checked[1] < .11
