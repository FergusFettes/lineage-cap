"""Independent exact moments and existing-model limits for duration scatter."""

import math

import pytest
import numpy as np

from lineage_cap.duration_spread import (completion_cdf, duration_bound, saturated_count,
                                       normal_completion_cdf, normal_cdf, normal_bound, normal_count)
from lineage_cap.expansion import C_MPC_PER_GYR, Geometry
from lineage_cap.history import History
from lineage_cap.start_spread import spread_bound


@pytest.mark.parametrize("w,d,delta", [(.1,.2,.04), (.1,.2,.15), (.1,.2,.25),
                                      (.1,.2,.5), (.2,1.36,.1)])
def test_radial_integral_matches_independent_average_sphere_volume(w, d, delta):
    g = Geometry()
    a = delta-g.delay(.5, "remote_visibility")
    # E[(a-U-V)_+^3], integrated directly over the rectangle in U,V.
    moment = (max(a,0)**5-max(a-w,0)**5-max(a-d,0)**5+max(a-w-d,0)**5)/(20*w*d)
    exact = 4*math.pi/3*g.galaxy_density*C_MPC_PER_GYR**3*moment
    assert saturated_count(delta,w,d,g,.5) == pytest.approx(exact, rel=1e-12)


@pytest.mark.parametrize("w", [.1,.2,1.0])
def test_zero_duration_scatter_recovers_existing_start_window(w):
    g, h = Geometry(), History()
    old = spread_bound(h,g,1,.5,"remote_visibility",w)
    new = duration_bound(w,0,g,.5,h.duration)
    assert new["lead_max_gyr"] == pytest.approx(float(old.lead.delta_max), abs=1e-9)
    assert new["completion_fraction_max"] == pytest.approx(float(old.percentile_max), abs=1e-8)


def test_cdf_uniform_convolution_and_symmetry():
    # Equal widths give a triangular completion density, not a uniform one.
    assert completion_cdf(.1,.2,.2) == pytest.approx(.125)
    assert completion_cdf(.2,.2,.2) == pytest.approx(.5)
    assert completion_cdf(.3,.2,.2) == pytest.approx(.875)
    assert completion_cdf(.15,.1,.2) == pytest.approx(.5)
    assert completion_cdf(.15,.2,.1) == pytest.approx(.5)
    assert completion_cdf(.1,0,.2) == pytest.approx(.5)


def test_caps_disabled_visibility_and_validation():
    g = Geometry()
    assert saturated_count(.2,.1,.2,g,0) == 0
    capped = duration_bound(.1,.2,Geometry(galaxy_density=0),.5,13.6)
    assert not capped["constrained_within_history"]
    assert capped["completion_fraction_max"] == 1
    assert duration_bound(0,0,g,.5,13.6)["completion_fraction_max"] is None
    with pytest.raises(ValueError):
        completion_cdf(.1,.2,-1)


def test_normal_start_convolution_against_direct_quadrature():
    nodes, weights = np.polynomial.legendre.leggauss(96)
    for t, location, sigma in [(.05,.1,.2), (13.6,18.8,1.36), (1,0,.3)]:
        w = .2
        length = min(t,w)
        u = length*(nodes+1)/2
        base = float(normal_cdf(-location/sigma))
        direct = length/(2*w)*np.dot(weights,(normal_cdf((t-u-location)/sigma)-base)/(1-base))
        assert normal_completion_cdf(t,w,location,sigma) == pytest.approx(direct, rel=1e-10)


def test_normal_zero_start_width_and_refined_boundary():
    assert normal_completion_cdf(1,0,1,.1) == pytest.approx(.5)
    g = Geometry()
    b = normal_bound(.2,1.36,g,.5,13.6)
    assert normal_count(b['normal_location_gyr'],1.36,.2,g,.5,13.6,384) == pytest.approx(-math.log(.05),rel=1e-7)
    assert 0 < b['completion_fraction_max'] < .001
