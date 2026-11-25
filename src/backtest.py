"""
The forecast put to the test: how well would its rules have done if they had been run before the months they
forecast, and how wide should the FY2027 figure be?

1. **Backtest.** At the end of each month of FY2026 from the third onwards, the forecast's own rules are run with
   only what was known that day: the leavers so far, annualised; the cost per FTE of the people on the payroll that
   day; the growth in the budget then in force; 90% of leavers replaced after TIME_TO_HIRE months. The result is
   set against the months that followed, and against two forecasts anyone could make without a model: the last
   month carried forward, and the budget.
2. **Interval.** The same rules simulated person by person: each month every person leaves with the cell's monthly
   probability, and the probability itself is drawn from what the leavers so far say about it (a gamma posterior
   on the leaving rate per person-year), so a cell with few leavers gets a wide interval. Backfills and growth
   follow the rules. The interval is checked on the backtest first (did the months that followed fall inside it?)
   and only then put on FY2027.

The actuals are the source organisation's own months (hr-people-analytics); every person keeps the same pay rate
through FY2026, so the test is about people, not pay. numpy for the simulation; the rest is the model's pandas.
"""
import numpy as np
import pandas as pd

import config as C
import model as M

FIRST_ORIGIN = 3          # the first month-end with enough leavers to annualise
DRAWS = 2000
LEVEL = 0.90              # interval coverage
SEED = 2027


def known_at(r: pd.DataFrame, act: pd.DataFrame, k: int) -> pd.DataFrame:
    """Per cell, what was known at the end of FY2026 month k: people, FTE, cost per FTE, leavers and exposure."""
    when = M.FY26[k - 1]
    rows = []
    for c, d in M.cells():
        g = r[(r["country"] == c) & (r["department"] == d)]
        a = M.active(g, when)
        left = g[(g["exit_key"] > M.OPENING) & (g["exit_key"] <= when)]
        avg_fte = act.loc[(act["country"] == c) & (act["department"] == d) & (act["month"] <= k), "fte"].mean()
        people = int(a.sum())
        heads = [M.active(g, M.FY26[m]).sum() for m in range(k)]
        fte = g.loc[a, "fte"].sum()
        rows.append({"country": c, "department": d, "people": people, "fte": fte,
                     "rate": g.loc[a, "loaded_cost"].sum() / fte if fte else 0.0,      # an empty cell costs nothing
                     "fte_per_head": fte / people if people else 0.0,
                     "leavers_fte": left["fte"].sum(), "leavers": len(left),
                     "attrition": left["fte"].sum() / avg_fte * 12 / k if avg_fte else 0.0,
                     "person_years": float(np.mean(heads)) * k / 12})
    return pd.DataFrame(rows)


def project(start: pd.DataFrame, months: int, growth: dict, merit_from: int | None = None) -> pd.DataFrame:
    """The forecast's rules on a starting position, month by month (the base case of model.forecast)."""
    rows = []
    for s in start.itertuples(index=False):
        a = s.attrition / 12
        g = growth[s.department]
        fte_prev, hist = s.fte, []
        for m in range(1, months + 1):
            leavers = fte_prev * a
            backfill = hist[m - 1 - C.TIME_TO_HIRE] if m > C.TIME_TO_HIRE else s.fte * a
            fte = fte_prev - leavers + backfill * 0.90 + s.fte * g / 12
            rate = s.rate * (1 + C.MERIT[s.country] * (merit_from is not None and m >= merit_from))
            rows.append({"country": s.country, "department": s.department, "month": m, "fte": fte,
                         "cost": fte * rate / 12})
            hist.append(leavers)
            fte_prev = fte
    return pd.DataFrame(rows)


def hiring_ratios(r: pd.DataFrame, act: pd.DataFrame, k: int) -> np.ndarray:
    """Company-wide, for FY2026 months 1..k: FTE actually hired over the FTE the rules would have hired."""
    hires = r[r["hire_date"] > M.OPENING]
    left = r[(r["exit_key"] > M.OPENING) & (r["exit_key"] <= M.CLOSING)]
    bounds = [M.OPENING, *M.FY26]
    hired = [hires.loc[(hires["hire_date"] > bounds[m]) & (hires["hire_date"] <= bounds[m + 1]), "fte"].sum()
             for m in range(k)]
    gone = [left.loc[(left["exit_key"] > bounds[m]) & (left["exit_key"] <= bounds[m + 1]), "fte"].sum()
            for m in range(k)]
    first = act[act["month"] == 1]
    growth = sum(first.loc[first["department"] == d, "fte"].sum() * C.BUDGET_GROWTH[d] for d in C.DEPARTMENTS) / 12
    steady = float(np.mean(gone))
    rule = [(gone[m - C.TIME_TO_HIRE] if m >= C.TIME_TO_HIRE else steady) * 0.90 + growth for m in range(k)]
    return np.array(hired) / np.array(rule)


def simulate(start: pd.DataFrame, months: int, growth: dict, rng: np.random.Generator, draws: int = DRAWS,
             merit_from: int | None = None, pace: np.ndarray | None = None) -> np.ndarray:
    """
    Total cost per month for each draw, shape (draws, months), the rules played out person by person.

    pace: hiring against the rules in the months seen so far (hiring_ratios). When given, each draw hires at a pace
    drawn around 1 with the spread those months show (their log ratios, resampled): the rules stay the centre, the
    months seen so far say how far hiring strays from them.
    """
    total = np.zeros((draws, months))
    mult = np.ones(draws)
    if pace is not None and len(pace) > 1:
        logs = np.log(pace)
        spread = logs - logs.mean()                      # how far a year's pace can stray, not where it went
        mult = np.exp(rng.choice(spread, size=(draws, len(spread))).mean(axis=1) * np.sqrt(len(spread)))
    for s in start.itertuples(index=False):
        # leaving rate per person-year: gamma posterior from the leavers so far (Jeffreys prior)
        lam = rng.gamma(s.leavers + 0.5, 1 / max(s.person_years, 1e-9), draws)
        p = 1 - np.exp(-lam / 12)
        heads = np.full(draws, float(s.people))
        hist = []
        growth_heads = s.people * growth[s.department] / 12
        for m in range(months):
            leavers = rng.binomial(heads.astype(np.int64), p).astype(float)
            backfill = hist[m - C.TIME_TO_HIRE] if m >= C.TIME_TO_HIRE else s.people * p
            hires = (backfill * 0.90 + growth_heads) * mult
            heads = heads - leavers + hires
            rate = s.rate * (1 + C.MERIT[s.country] * (merit_from is not None and m + 1 >= merit_from))
            total[:, m] += np.maximum(heads, 0) * s.fte_per_head * rate / 12
            hist.append(leavers)
    return total


def backtest(r: pd.DataFrame | None = None) -> dict:
    r = M.roster() if r is None else r
    act = M.actuals(r)
    bud = M.budget(r)
    rng = np.random.default_rng(SEED)
    tail = (1 - LEVEL) / 2 * 100
    rows, by_month = [], []
    for k in range(FIRST_ORIGIN, C.MONTHS):
        h = C.MONTHS - k
        start = known_at(r, act, k)
        f = project(start, h, C.BUDGET_GROWTH)
        f["month"] += k
        truth = act[act["month"] > k]
        last = act[act["month"] == k]
        sims = simulate(start, h, C.BUDGET_GROWTH, rng)
        lo, hi = np.percentile(sims.sum(axis=1), [tail, 100 - tail])
        paced = simulate(start, h, C.BUDGET_GROWTH, rng, pace=hiring_ratios(r, act, k)).sum(axis=1)
        plo, phi = np.percentile(paced, [tail, 100 - tail])
        actual = float(truth["cost"].sum())
        row = {"origin": k, "horizon": h, "actual": actual, "model": float(f["cost"].sum()),
               "naive": float(last["cost"].sum()) * h,
               "budget": float(bud.loc[bud["month"] > k, "cost"].sum()), "low": float(lo), "high": float(hi),
               "pace_low": float(plo), "pace_high": float(phi)}
        rows.append(row)
        mt = truth.groupby("month")[["fte", "cost"]].sum()
        mf = f.groupby("month")[["fte", "cost"]].sum()
        mlo, mhi = np.percentile(sims, [tail, 100 - tail], axis=0)
        for i, m in enumerate(mt.index):
            by_month.append({"origin": k, "month": m, "ahead": m - k, "actual": mt.loc[m, "cost"],
                             "model": mf.loc[m, "cost"], "naive": float(last["cost"].sum()),
                             "budget": float(bud.loc[bud["month"] == m, "cost"].sum()),
                             "low": mlo[i], "high": mhi[i], "actual_fte": mt.loc[m, "fte"],
                             "model_fte": mf.loc[m, "fte"]})
    t, bm = pd.DataFrame(rows), pd.DataFrame(by_month)
    for col in ("model", "naive", "budget"):
        t[f"err_{col}"] = t[col] / t["actual"] - 1
        bm[f"err_{col}"] = bm[col] / bm["actual"] - 1
    t["inside"] = (t["actual"] >= t["low"]) & (t["actual"] <= t["high"])
    t["inside_pace"] = (t["actual"] >= t["pace_low"]) & (t["actual"] <= t["pace_high"])
    bm["inside"] = (bm["actual"] >= bm["low"]) & (bm["actual"] <= bm["high"])
    ahead = bm.groupby("ahead").agg(**{f"mape_{c}": (f"err_{c}", lambda e: float(np.mean(np.abs(e))))
                                       for c in ("model", "naive", "budget")},
                                    coverage=("inside", "mean"), n=("inside", "size")).reset_index()
    return {"origins": t, "months": bm, "ahead": ahead}


def fy2027_interval(r: pd.DataFrame | None = None, base_total: float | None = None) -> dict:
    """The base case's FY2027 payroll with an interval, from the full year of FY2026 leavers."""
    r = M.roster() if r is None else r
    act = M.actuals(r)
    start = known_at(r, act, C.MONTHS)
    rng = np.random.default_rng(SEED + 1)
    central = project(start, C.MONTHS, C.FORECAST_GROWTH, merit_from=C.MERIT_MONTH)
    tail = (1 - LEVEL) / 2 * 100
    sims = simulate(start, C.MONTHS, C.FORECAST_GROWTH, rng, merit_from=C.MERIT_MONTH).sum(axis=1)
    lo, hi = np.percentile(sims, [tail, 100 - tail])
    paced = simulate(start, C.MONTHS, C.FORECAST_GROWTH, rng, merit_from=C.MERIT_MONTH,
                     pace=hiring_ratios(r, act, C.MONTHS)).sum(axis=1)
    plo, pmid, phi = np.percentile(paced, [tail, 50, 100 - tail])
    return {"central": float(central["cost"].sum()), "low": float(lo), "high": float(hi),
            "pace_low": float(plo), "pace_median": float(pmid), "pace_high": float(phi), "base_total": base_total}


if __name__ == "__main__":
    b = backtest()
    pd.set_option("display.width", 200)
    print(b["origins"].round(4).to_string())
    print(b["ahead"].round(4).to_string())
    print(fy2027_interval())
