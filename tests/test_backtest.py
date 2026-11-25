"""The backtest uses only what was known at each origin, the projection is the model's own base case, and the
intervals behave."""
import numpy as np
import pandas as pd
import pytest

import backtest as B
import config as C
import model as M


@pytest.fixture(scope="module")
def r():
    return M.roster()


@pytest.fixture(scope="module")
def act(r):
    return M.actuals(r)


def test_projection_is_the_base_case_forecast(r, act):
    start = B.known_at(r, act, C.MONTHS)
    mine = B.project(start, C.MONTHS, C.FORECAST_GROWTH, merit_from=C.MERIT_MONTH)
    base = M.forecast(r, act, C.SCENARIOS[0])[0]
    assert C.SCENARIOS[0][2] == 0.90 and C.SCENARIOS[0][1] == 1.0
    assert np.allclose(mine["fte"].to_numpy(), base["fte"].to_numpy())
    assert mine["cost"].sum() == pytest.approx(base["cost"].sum(), rel=1e-12)


def test_known_at_ignores_the_future(r, act):
    k = 6
    later = r.copy()
    after = later["exit_key"] > M.FY26[k - 1]
    later.loc[after, "exit_key"] = M.FAR_FUTURE           # nobody leaves after the origin
    a, b = B.known_at(r, act, k), B.known_at(later, act, k)
    pd.testing.assert_frame_equal(a, b)


def test_hiring_ratios_cover_the_months_seen(r, act):
    for k in (3, 6, 12):
        ratios = B.hiring_ratios(r, act, k)
        assert len(ratios) == k and (ratios > 0).all()


def test_no_leavers_and_no_growth_means_no_spread():
    start = pd.DataFrame([{"country": "IT", "department": "HR", "people": 40, "fte": 40.0, "rate": 60000.0,
                           "fte_per_head": 1.0, "leavers": 0, "leavers_fte": 0.0, "attrition": 0.0,
                           "person_years": 1e12}])
    sims = B.simulate(start, 3, {"HR": 0.0}, np.random.default_rng(0), draws=50)
    assert np.allclose(sims, 40 * 60000 / 12)


def test_backtest_results_hold():
    b = B.backtest()
    o, a = b["origins"], b["ahead"]
    assert len(o) == C.MONTHS - B.FIRST_ORIGIN
    assert (a["mape_model"] < a["mape_budget"]).all()
    assert (a["mape_model"] <= a["mape_naive"]).all()
    assert o["inside_pace"].sum() > o["inside"].sum()      # hiring pace is the uncertainty that matters


def test_fy2027_interval_contains_the_base_case():
    iv = B.fy2027_interval()
    assert iv["low"] < iv["central"] < iv["high"]
    assert iv["pace_low"] < iv["low"] and iv["high"] < iv["pace_high"]
