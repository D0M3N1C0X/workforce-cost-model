"""The pandas model obeys its own definitions: cost rules, the variance split and the forecast recursion."""
import pytest

import config as C
import model

APPROX = dict(rel=1e-12, abs=1e-6)


def test_source_file_is_the_pinned_one(monkeypatch):
    model.verify_source()
    monkeypatch.setattr(C, "SOURCE_SHA256", "0" * 64)
    with pytest.raises(SystemExit):
        model.verify_source()


def test_roster_covers_both_entities_over_fy2026(out):
    r = out["roster"]
    assert set(r["country"]) == set(C.ENTITIES)
    assert r["employee_id"].is_unique
    assert (r["hire_date"] <= model.CLOSING).all()
    assert (r["exit_key"] > model.OPENING).all()


def test_loaded_cost_is_gross_plus_social_plus_tfr(out):
    r = out["roster"]
    assert (r["gross"] - r["base"] - r["bonus"]).abs().max() < 1e-9
    assert (r["loaded_cost"] - r["gross"] - r["employer_social"] - r["tfr"]).abs().max() < 1e-9


def test_italian_contributions(out):
    it = out["roster"].query("country == 'IT'")
    expected = it["gross"] * (C.IT_IVS + C.IT_OTHER)
    assert (it["employer_social"] - expected).abs().max() < 1e-6
    assert (it["tfr"] - it["base"] / C.TFR_DIVISOR).abs().max() < 1e-9


def test_polish_pension_and_disability_stop_at_the_cap(out):
    pl = out["roster"].query("country == 'PL'")
    assert (pl["tfr"] == 0).all()
    uncapped = C.PL_ACCIDENT + C.PL_LABOUR_FUND + C.PL_FGSP + C.PL_PPK * C.PPK_PARTICIPATION
    capped = C.PL_PENSION + C.PL_DISABILITY
    cap = C.PL_CAP_PLN / C.EUR_PLN
    expected = pl["gross"].clip(upper=cap) * capped + pl["gross"] * uncapped
    assert (pl["employer_social"] - expected).abs().max() < 1e-6
    above = pl[pl["gross"] > cap]
    assert len(above) > 0, "the sample has no one above the cap, so the cap is not exercised"
    assert (above["employer_social"] < above["gross"] * (capped + uncapped)).all()


def test_no_polish_salary_below_the_minimum_wage(out):
    pl = out["roster"].query("country == 'PL'")
    assert model.pl_min_wage_eur() == pytest.approx(4806 * 12 / 4.2568)
    assert (pl["salary"] >= model.pl_min_wage_eur()).all()


def test_actuals_count_the_payroll_at_each_month_end(out):
    act, r = out["actuals"], out["roster"]
    assert len(act) == len(model.cells()) * C.MONTHS
    june = act[act["month"] == C.MONTHS]
    on_payroll = r[model.active(r, model.CLOSING)]
    assert june["fte"].sum() == pytest.approx(on_payroll["fte"].sum(), **APPROX)
    assert june["cost"].sum() == pytest.approx(on_payroll["loaded_cost"].sum() / 12, **APPROX)
    assert out["start"]["fte"].sum() == pytest.approx(june["fte"].sum(), **APPROX)


def test_budget_grows_from_the_opening_population(out):
    bud, start = out["budget"], model.opening(out["roster"], model.OPENING)
    for s in start.itertuples():
        b = bud[(bud["country"] == s.country) & (bud["department"] == s.department)].set_index("month")
        g = C.BUDGET_GROWTH[s.department]
        assert b.loc[12, "fte"] == pytest.approx(s.fte * (1 + g), **APPROX)
        assert (b["cost"] - b["fte"] * s.rate / 12).abs().max() < 1e-6


def test_department_variance_is_volume_plus_rate(out):
    v = out["variance_dept"]
    assert (v["volume"] + v["rate"] - v["variance"]).abs().max() < 1e-6


def test_entity_variance_is_volume_plus_mix_plus_rate(out):
    e, v = out["variance_entity"], out["variance_dept"]
    assert (e["volume"] + e["mix"] + e["rate"] - e["variance"]).abs().max() < 1e-6
    by_entity = v.groupby("country")[["volume", "rate", "variance"]].sum()
    for row in e.itertuples():
        assert row.volume + row.mix == pytest.approx(by_entity.loc[row.country, "volume"], **APPROX)
        assert row.variance == pytest.approx(by_entity.loc[row.country, "variance"], **APPROX)


def test_forecast_rolls_fte_forward(out):
    for name, (f, _) in out["forecasts"].items():
        for _, g in f.groupby(["country", "department"]):
            g = g.sort_values("month")
            prev = g["fte"].shift(1)
            roll = prev - g["leavers"] + g["hires"]
            assert (roll.iloc[1:] - g["fte"].iloc[1:]).abs().max() < 1e-9, name
            assert (g["leavers"] >= 0).all() and (g["hires"] >= 0).all()


def test_backfills_start_after_the_time_to_hire(out):
    f, _ = out["forecasts"]["Base"]
    replacement = next(s[2] for s in C.SCENARIOS if s[0] == "Base")
    attr = out["attrition"].set_index(["country", "department"])["rate"]
    start = out["start"].set_index(["country", "department"])["fte"]
    for (c, d), g in f.groupby(["country", "department"]):
        g = g.set_index("month")
        growth_hires = start[(c, d)] * C.FORECAST_GROWTH[d] / 12
        # before the first backfill is due, hires replace leavers at the FY2026 rate
        assert g.loc[1, "hires"] == pytest.approx(start[(c, d)] * attr[(c, d)] / 12 * replacement + growth_hires,
                                                  **APPROX)
        # afterwards, month m replaces the leavers of month m - time to hire
        for m in range(C.TIME_TO_HIRE + 1, C.MONTHS + 1):
            expected = g.loc[m - C.TIME_TO_HIRE, "leavers"] * replacement + growth_hires
            assert g.loc[m, "hires"] == pytest.approx(expected, **APPROX)


def test_frozen_months_have_no_hires(out):
    f, _ = out["forecasts"]["Hiring freeze"]
    frozen_from = next(s[4] for s in C.SCENARIOS if s[0] == "Hiring freeze")
    assert (f.loc[f["month"] >= frozen_from, "hires"] == 0).all()
    assert (f.loc[f["month"] < frozen_from, "hires"] > 0).any()


def test_pay_review_applies_from_its_month(out):
    f, _ = out["forecasts"]["Base"]
    start = out["start"].set_index(["country", "department"])["rate"]
    for row in f.itertuples():
        rate = start[(row.country, row.department)] * (1 + C.MERIT[row.country] * (row.month >= C.MERIT_MONTH))
        assert row.cost == pytest.approx(row.fte * rate / 12, **APPROX)


def test_remediation_only_in_its_scenario_and_months(out):
    for name, (_, rem) in out["forecasts"].items():
        start = next(s[5] for s in C.SCENARIOS if s[0] == name)
        if not start:
            assert (rem["remediation"] == 0).all(), name
            continue
        assert (rem.loc[rem["month"] < start, "remediation"] == 0).all()
        for c in C.ENTITIES:
            total = rem.loc[rem["country"] == c, "remediation"].sum()
            months = C.MONTHS - start + 1
            assert total == pytest.approx(C.REMEDIATION[c] * model.loaded_factor(c) * months / 12, **APPROX)


def test_bridge_adds_up_to_the_change_in_cost(out):
    s = out["summary"]
    change = s["fy27_cost"] - s["fy26_cost"]
    bridge = s["bridge_volume"] + s["bridge_rate"] + s["bridge_remediation"]
    assert (bridge - change).abs().max() < 1e-6
    assert (s["fy27_cost"] - s["fy27_payroll"] - s["fy27_remediation"]).abs().max() < 1e-6


def test_scenarios_move_in_the_expected_direction(out):
    tot = out["summary"].groupby("scenario")[["fy27_cost", "fy27_hiring_cost", "closing_fte"]].sum()
    assert tot["fy27_cost"].idxmin() == "Hiring freeze"
    assert tot.loc["Hiring freeze", "closing_fte"] < tot.loc["Base", "closing_fte"]
    assert tot.loc["High attrition", "fy27_hiring_cost"] > tot.loc["Base", "fy27_hiring_cost"]
    assert tot.loc["Pay equity first", "fy27_cost"] > tot.loc["Base", "fy27_cost"]


def test_model_runs_on_a_subset():
    import check_workbook
    sub = check_workbook.sample(1, seed=3)
    o = model.run(sub)
    assert len(o["roster"]) == len(sub)
    assert o["summary"]["fy27_cost"].gt(0).all()
