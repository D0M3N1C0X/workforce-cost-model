"""The figures quoted in the README and in docs/method.md are the ones the model produces."""
from pathlib import Path

import build_memo as B
import build_workbook
import config as C
import model

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
METHOD = (ROOT / "docs" / "method.md").read_text(encoding="utf-8")


def test_readme_quotes_current_figures(out, tmp_path):
    f = B.facts(out)
    ve, base, freeze, high, equity = f["ve"], f["base"], f["freeze"], f["high"], f["equity"]
    r = out["roster"]
    snap = r[model.active(r, model.CLOSING)]
    per_fte = {c: g["loaded_cost"].sum() / g["fte"].sum() for c, g in snap.groupby("country")}
    full_year = sum(C.REMEDIATION[c] * model.loaded_factor(c) for c in C.ENTITIES)
    n_checks = len(build_workbook.build(out, tmp_path / "m.xlsx").checks)
    expected = [
        f"FY2026 closed {B.m(ve['variance'].sum())} ({B.pct(ve['variance'].sum() / ve['budget_cost'].sum())}) "
        f"over budget, at {B.m(base['fy26_cost'])}",
        f"{base['fy26_fte']:,.0f} FTE on average",
        f"added {B.m(ve['volume'].sum())}",
        f"€{per_fte['IT']:,.0f} per FTE in Milan and €{per_fte['PL']:,.0f} in Kraków",
        f"{f['above_cap']} people earn above the {C.PL_CAP_PLN:,} PLN cap",
        f"FY2027 costs {B.m(base['fy27_cost'])} in the base case ({B.signed(base['fy27_cost'] / base['fy26_cost'] - 1)})",
        f"cuts it to {B.m(freeze['fy27_cost'])}",
        f"{base['closing_fte'] - freeze['closing_fte']:,.0f} fewer FTE",
        f"recruitment cost to {B.m(high['fy27_hiring_cost'], 2)}",
        f"adds {B.m(equity['fy27_remediation'], 2)}** to FY2027 and {B.m(full_year, 2)} a year after",
        f"reconciled on {n_checks} checks",
    ]
    missing = [e for e in expected if e not in README]
    assert not missing, f"README is out of date: {missing}"
    assert f"{n_checks} checks" in METHOD, "docs/method.md quotes a stale number of checks"


def test_scenario_months_in_the_docs_match_the_settings():
    months = model.month_ends(C.FY2027_START)
    freeze = next(s[4] for s in C.SCENARIOS if s[0] == "Hiring freeze")
    equity = next(s[5] for s in C.SCENARIOS if s[0] == "Pay equity first")
    assert f"from {months[freeze - 1]:%B %Y}" in METHOD
    assert f"from {months[equity - 1]:%B %Y}" in METHOD
    assert f"freeze from {months[freeze - 1]:%B}" in README
    assert f"from {months[equity - 1]:%B %Y} adds" in README
