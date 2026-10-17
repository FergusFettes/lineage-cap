"""Closed-form checks for the hard-steps lottery and the late-filter q ceiling."""

import math

import numpy as np
import pytest

from lineage_cap import iid_tail
from lineage_cap.expansion import C_MPC_PER_GYR, Geometry
from lineage_cap.history import History
from lineage_cap.observer_rates import HardSteps, hard_steps_boundary, q_ceiling


@pytest.mark.parametrize("n", [3, 6, 9])
def test_hard_steps_without_window_matches_beta_integral(n):
    # Rare limit: mu = 4 pi n_g c^3 B k / (n+1) * X^(n+4) * Beta(3, n+2).
    history = History.from_config(iid_tail.CONFIG)
    geometry = Geometry.from_config(iid_tail.CONFIG)
    model = HardSteps(n, math.inf, history)
    k = hard_steps_boundary(model, history, geometry)
    span = history.now - geometry.delay(iid_tail.SPEED_C, "remote_visibility") - history.start
    beta = 2 * math.factorial(n + 1) / math.factorial(n + 4)
    n_g = float(iid_tail.CONFIG["abundance"]["galaxy_density_mpc3"])
    exact = iid_tail.MU_STAR * (n + 1) / (
        4 * math.pi * n_g * C_MPC_PER_GYR**3 * model.birth_rate * span ** (n + 4) * beta
    )
    assert k == pytest.approx(exact, rel=1e-6)


def test_hard_steps_expected_is_integral_of_rate():
    history = History.from_config(iid_tail.CONFIG)
    model = HardSteps(6, 5.0, history)
    t = np.linspace(history.start, history.now, 200001)
    integral = np.trapezoid(model.rate(t, 1e-3), t)
    assert model.expected(np.array([history.now]), 1e-3)[0] == pytest.approx(integral, rel=1e-6)


def test_q_ceiling_at_q_one_recovers_iid_boundary():
    history = History.from_config(iid_tail.CONFIG)
    geometry = Geometry.from_config(iid_tail.CONFIG)
    z0 = iid_tail.solve_z(0.136, history, geometry)
    assert q_ceiling(0.136, z0, history, geometry) == pytest.approx(1.0, rel=1e-6)
