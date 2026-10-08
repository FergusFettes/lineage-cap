"""Check the physical budget against independent numerical integration."""

import numpy as np
import pytest

from lineage_cap.history import History


@pytest.mark.parametrize("alpha,beta", [(1, 1), (1, 0), (0, 1), (1.7, .6)])
def test_integrated_budget_matches_quadrature(alpha, beta):
    h = History(alpha=alpha, beta=beta)
    time = np.linspace(h.start, h.now, 100001)
    numerical = np.trapezoid(h.total_capacity(time), time)
    assert h.spacetime(h.now) == pytest.approx(numerical, rel=1e-8)


@pytest.mark.parametrize("alpha,beta", [(1, 1), (1, 0), (1.7, .6)])
def test_cohort_exposures_conserve_total_opportunity(alpha, beta):
    h = History(alpha=alpha, beta=beta)
    birth, numbers = h.cohorts(bins=10000)
    assert numbers.sum() == pytest.approx(h.zones_now)
    # Each cohort accumulates only after birth; sum equals the galactic integral.
    total = np.dot(numbers, h.exposure(birth, h.now))
    assert total == pytest.approx(h.spacetime(h.now), rel=1e-7)


def test_no_prebirth_or_prestart_exposure():
    h = History()
    assert np.all(h.spacetime([-1, 0, h.start]) == 0)
    assert np.all(h.exposure(9.2, [1, 9.2]) == 0)


def test_units_scale_with_capacity_and_population_separately():
    h = History()
    more_zones = History(zones_now=3 * h.zones_now)
    more_capacity = History(capacity_now=4 * h.capacity_now)
    assert more_zones.spacetime(h.now) == pytest.approx(3 * h.spacetime(h.now))
    assert more_zones.exposure(9.2, h.now) == h.exposure(9.2, h.now)
    assert more_capacity.exposure(9.2, h.now) == pytest.approx(4 * h.exposure(9.2, h.now))
