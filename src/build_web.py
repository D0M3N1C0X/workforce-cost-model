"""
Writes what the scenario simulator needs (web/inputs.json, a roster template) and the cases its JavaScript is
checked against (tests/fixtures/js_vectors.json), each computed here by the model. tests/js/check_engine.mjs
recomputes them with web/engine.js and fails at the first difference.
"""
import json
import random
from contextlib import contextmanager

import pandas as pd

import config as C
import employer_cost as E
import model

WEB = C.ROOT / "web"
VECTORS = C.ROOT / "tests" / "fixtures" / "js_vectors.json"
NAMES = ["name", "attrition_x", "replacement", "growth_x", "freeze_from", "remediation_from", "renewal", "eur_pln"]
CLOSED = ["country", "department", "month", "fte", "leavers", "hires", "cost"]


def rules() -> dict:
    """Every rate and ceiling of the four countries, by the name config.py gives it."""
    extra = ("TFR_DIVISOR", "EUR_PLN", "PPK_PARTICIPATION")
    keys = [k for k in dir(C) if k[:3] in ("IT_", "PL_", "DE_", "ES_") or k in extra]
    return {k: getattr(C, k) for k in sorted(keys)}


def sample(out: dict) -> dict:
    """The sample company as the simulator starts from it: the opening cells of FY2027 with their attrition and
    growth, and FY2026 actuals per entity for the bridge."""
    attr = out["attrition"].set_index(["country", "department"])["rate"]
    act = out["actuals"]
    return {
        "cells": [{"country": s.country, "department": s.department, "fte": s.fte, "rate": s.rate,
                   "attrition": attr[(s.country, s.department)], "growth": C.FORECAST_GROWTH[s.department]}
                  for s in out["start"].itertuples(index=False)],
        "baseline": {c: {"fte": act[act["country"] == c].groupby("month")["fte"].sum().mean(),
                         "cost": act.loc[act["country"] == c, "cost"].sum()} for c in C.ENTITIES},
        "remediation": C.REMEDIATION,
        "summary": out["summary"][out["summary"]["scenario"] == "Base"].to_dict("records"),
        "closed": out["ytd"][CLOSED].to_dict("records"),
        "outlook_summary": out["outlook_summary"].to_dict("records"),
    }


def cfg() -> dict:
    return {"rules": rules(), "countries": E.COUNTRIES, "entities": C.ENTITIES, "months": C.MONTHS,
            "fy2027_start": C.FY2027_START.isoformat(), "merit": C.MERIT, "merit_month": C.MERIT_MONTH,
            "time_to_hire": C.TIME_TO_HIRE, "cost_per_hire": C.COST_PER_HIRE, "eur_pln": C.EUR_PLN,
            "renewal": {c: list(v) for c, v in C.RENEWAL.items()}, "plan_target": C.PLAN_TARGET,
            "loaded_factor": {c: E.loaded_factor(c) for c in E.COUNTRIES},
            "scenarios": [dict(zip(NAMES, s, strict=True)) for s in C.SCENARIOS],
            "bonus_target": C.BONUS_TARGET, "client": C.CLIENT_DEFAULTS}


def write_inputs(out: dict) -> None:
    WEB.mkdir(exist_ok=True)
    (WEB / "inputs.json").write_text(json.dumps({"cfg": cfg(), "sample": sample(out)}, indent=1, ensure_ascii=False)
                                     + "\n", encoding="utf-8")
    pd.DataFrame([["E001", "IT", "Sales", 1.0, 42000, 3000], ["E002", "DE", "Tech", 0.8, 68000, 0],
                  ["E003", "ES", "Finance", 1.0, 39000, 1500]],
                 columns=["employee_id", "country", "department", "fte", "base_salary", "bonus"]).to_csv(
        WEB / "template_roster.csv", index=False)


@contextmanager
def settings(**kw: object):
    """Run the model with some settings changed, then put them back."""
    old = {k: getattr(C, k) for k in kw}
    try:
        for k, v in kw.items():
            setattr(C, k, v)
        yield
    finally:
        for k, v in old.items():
            setattr(C, k, v)


def _forecast(out: dict, scenario: tuple) -> dict:
    f, rem = model.forecast(out["roster"], out["actuals"], scenario)
    s = model.summary(out["actuals"], {scenario[0]: (f, rem)})
    return {"months": f[["country", "department", "month", "fte", "hires", "cost", "hiring_cost"]].values.tolist(),
            "remediation": rem[["country", "month", "remediation"]].values.tolist(),
            "summary": s.drop(columns="scenario").to_dict("records")}


def _outlook(out: dict, closed: pd.DataFrame) -> dict:
    """The outlook and plan from the given closed months, with the settings in force, for the JavaScript twin."""
    k = int(closed["month"].max()) if len(closed) else 0
    om, oc = model.outlook(out["roster"], out["actuals"], closed)
    pm, pc = model.plan(om, oc, k)
    budget = model.forecast(out["roster"], out["actuals"], C.SCENARIOS[0])[0]
    cols = ["country", "department", "month", "fte", "leavers", "hires", "cost", "hiring_cost"]
    return {"closed": closed[CLOSED].to_dict("records"), "merit": dict(C.MERIT), "time_to_hire": C.TIME_TO_HIRE,
            "merit_month": C.MERIT_MONTH,
            "plan_target": dict(C.PLAN_TARGET),
            "budget": budget[cols].to_dict("records"), "outlook": om[cols].values.tolist(),
            "outlook_cells": oc.to_dict("records"), "plan": pm[cols].values.tolist(), "plan_cells": pc.to_dict("records"),
            "summary": model.outlook_summary(budget, om, pm, pc, k).to_dict("records")}


def write_vectors(out: dict, n: int = 8, seed: int = 27) -> int:
    rng = random.Random(seed)
    cases = [{"scenario": dict(zip(NAMES, s, strict=True)), "merit": C.MERIT, "time_to_hire": C.TIME_TO_HIRE,
              **_forecast(out, s)} for s in C.SCENARIOS]
    for k in range(n):
        s = (f"Random {k}", rng.choice([0.5, 0.8, 1.0, 1.3, 2.0]), rng.choice([0.0, 0.5, 0.9, 1.0]),
             rng.choice([0.0, 0.5, 1.0, 2.0]), rng.choice([0, 1, 4, 9, 12]), rng.choice([0, 1, 7, 12]),
             rng.choice([0, 1]), rng.choice([3.9, 4.0, C.EUR_PLN, 4.6]))
        merit = {c: rng.choice([0.0, 0.02, 0.035, 0.06]) for c in C.ENTITIES}
        renewal = {c: (rng.choice([0.0, 0.01, 0.025]), rng.choice([0, 1, 5, 12])) for c in C.ENTITIES}
        tth = rng.choice([1, 2, 3, 6])
        with settings(MERIT=merit, TIME_TO_HIRE=tth, RENEWAL=renewal):
            cases.append({"scenario": dict(zip(NAMES, s, strict=True)), "merit": merit, "time_to_hire": tth,
                          "renewal": {c: list(v) for c, v in renewal.items()}, **_forecast(out, s)})
    # the outlook and the plan: the sample's closed months, fewer of them, none, and other settings
    ytd = out["ytd"]
    outlooks = [_outlook(out, ytd), _outlook(out, ytd[ytd["month"] <= 2]), _outlook(out, ytd.iloc[0:0])]
    for _ in range(3):
        target = {d: rng.choice([-0.2, -0.05, 0.0, 0.08, 0.3]) for d in C.DEPARTMENTS}
        merit = {c: rng.choice([0.0, 0.03]) for c in C.ENTITIES}
        with settings(TIME_TO_HIRE=rng.choice([1, 3, 8, 11]), PLAN_TARGET=target, MERIT=merit,
                      MERIT_MONTH=rng.choice([1, 3, 7])):
            outlooks.append(_outlook(out, ytd))
    # employer cost: every country, around every ceiling
    grid = sorted({round(x, 2) for x in [0, 1, 12_000, 30_000, 50_000, C.ES_CAP, C.ES_CAP + 1, 67_335.84,
                                         C.DE_CAP_HEALTH, 80_000, 91_821.6, 95_000, C.DE_CAP_PENSION,
                                         C.PL_CAP_PLN / C.EUR_PLN, 70_000.5, 150_000, 400_000]})
    costs = [[c, g, E.items(c, g, g * 0.9), E.total(c, g, g * 0.9)] for c in E.COUNTRIES for g in grid]
    # a client's roster: the cells the simulator builds from it
    src = pd.read_csv(C.SOURCE_EMPLOYEES).sample(400, random_state=seed).reset_index(drop=True)
    roster = pd.DataFrame({"country": src["country"], "department": src["department"], "fte": src["fte"],
                           "base": src["base_salary_eur"], "bonus": (src["base_salary_eur"] * 0.05).round(2)})
    roster["gross"] = roster["base"] * roster["fte"] + roster["bonus"]
    roster["loaded"] = [E.total(c, g, b * f) for c, g, b, f in zip(roster["country"], roster["gross"], roster["base"],
                                                                   roster["fte"], strict=True)]
    cells = roster.groupby(["country", "department"], sort=False).agg(fte=("fte", "sum"), cost=("loaded", "sum"))
    cells["rate"] = cells["cost"] / cells["fte"]
    VECTORS.parent.mkdir(exist_ok=True)
    people = roster[["country", "department", "fte", "base", "bonus"]].to_dict("records")
    VECTORS.write_text(json.dumps({"cfg": cfg(), "sample": sample(out), "cases": cases, "outlooks": outlooks,
                                   "costs": costs,
                                   "roster": people,
                                   "cells": cells.reset_index().to_dict("records")},
                                  ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return len(cases)


def main() -> None:
    out = model.run()
    write_inputs(out)
    print(f"simulator -> web/inputs.json; {write_vectors(out)} cases -> tests/fixtures/js_vectors.json")


if __name__ == "__main__":
    main()
