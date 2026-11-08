"""
The workforce cost model in pandas. Every function has a twin in the Excel workbook built by
build_workbook.py, written with the same order of operations so the two agree.

    roster()      one row per employee of the four entities, with the fully loaded annual cost
    actuals()     FY2026 month-end FTE and cost, by entity and department
    budget()      the FY2026 plan
    variance()    FY2026 actual against budget: volume, mix and rate
    forecast()    FY2027 month by month, for each scenario
    outlook()     FY2027 after the closed months: actuals so far, then a re-forecast from the run-rate (4+8)
    plan()        the hires a month it takes to land on the June 2027 headcount target, and their cost
"""
import calendar
import hashlib
from datetime import date

import pandas as pd

import config as C
import employer_cost as E
import ytd

FAR_FUTURE = pd.Timestamp("2099-12-31")


def month_ends(start: date, n: int = C.MONTHS) -> list[pd.Timestamp]:
    out = []
    y, m = start.year, start.month
    for _ in range(n):
        out.append(pd.Timestamp(y, m, calendar.monthrange(y, m)[1]))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


FY26 = month_ends(C.FY2026_START)
OPENING = pd.Timestamp(C.FY2026_START) - pd.Timedelta(days=1)      # 30 June 2025
CLOSING = FY26[-1]                                                  # 30 June 2026


def verify_source() -> None:
    digest = hashlib.sha256(C.SOURCE_EMPLOYEES.read_bytes()).hexdigest()
    if digest != C.SOURCE_SHA256:
        raise SystemExit(f"{C.SOURCE_EMPLOYEES} does not match the pinned checksum")


def pl_cap_eur() -> float:
    return C.PL_CAP_PLN / C.EUR_PLN


def pl_min_wage_eur() -> float:
    """The 2026 Polish minimum wage for a year of full-time work, in euro."""
    return C.PL_MIN_WAGE_PLN * 12 / C.EUR_PLN


def roster() -> pd.DataFrame:
    """Everyone employed by one of the four entities at any point of FY2026."""
    verify_source()
    e = pd.read_csv(C.SOURCE_EMPLOYEES, parse_dates=["hire_date", "exit_date"])
    e = e[e["country"].isin(list(C.ENTITIES))]
    e = e[(e["hire_date"] <= CLOSING) & (e["exit_date"].isna() | (e["exit_date"] > OPENING))]
    e = e.sort_values("employee_id").reset_index(drop=True)
    r = pd.DataFrame({
        "employee_id": e["employee_id"],
        "country": e["country"],
        "department": e["department"],
        "job_level": e["job_level"],
        "fte": e["fte"],
        "salary": e["base_salary_eur"],
        "hire_date": e["hire_date"],
        "exit_date": e["exit_date"],
    })
    r["exit_key"] = r["exit_date"].fillna(FAR_FUTURE)
    r["base"] = r["salary"] * r["fte"]
    r["bonus"] = r["base"] * r["job_level"].map(C.BONUS_TARGET)
    r["gross"] = r["base"] + r["bonus"]
    # employer contributions with each country's ceilings (employer_cost.items, the calculator's rules); the TFR is
    # Italy's only non-contribution item
    items = [E.items(c, g, b) for c, g, b in zip(r["country"], r["gross"], r["base"], strict=True)]
    r["employer_social"] = [sum(v for k, v in i.items() if k != "tfr") for i in items]
    r["tfr"] = [i.get("tfr", 0.0) for i in items]
    r["loaded_cost"] = r["gross"] + r["employer_social"] + r["tfr"]
    return r


def active(r: pd.DataFrame, when: pd.Timestamp) -> pd.Series:
    return (r["hire_date"] <= when) & (r["exit_key"] > when)


def cells() -> list[tuple[str, str]]:
    return [(c, d) for c in C.ENTITIES for d in C.DEPARTMENTS]


def actuals(r: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c, d in cells():
        g = r[(r["country"] == c) & (r["department"] == d)]
        for m, end in enumerate(FY26, start=1):
            a = active(g, end)
            rows.append({"country": c, "department": d, "month": m,
                         "fte": g.loc[a, "fte"].sum(), "cost": g.loc[a, "loaded_cost"].sum() / 12})
    return pd.DataFrame(rows)


def opening(r: pd.DataFrame, when: pd.Timestamp) -> pd.DataFrame:
    rows = []
    for c, d in cells():
        g = r[(r["country"] == c) & (r["department"] == d)]
        a = active(g, when)
        fte = g.loc[a, "fte"].sum()
        rows.append({"country": c, "department": d, "fte": fte, "rate": g.loc[a, "loaded_cost"].sum() / fte})
    return pd.DataFrame(rows)


def budget(r: pd.DataFrame) -> pd.DataFrame:
    base = opening(r, OPENING)
    rows = []
    for b in base.itertuples(index=False):
        g = C.BUDGET_GROWTH[b.department]
        for m in range(1, C.MONTHS + 1):
            fte = b.fte * (1 + g * m / 12)
            rows.append({"country": b.country, "department": b.department, "month": m,
                         "fte": fte, "cost": fte * b.rate / 12})
    return pd.DataFrame(rows)


def variance(act: pd.DataFrame, bud: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    key = ["country", "department"]
    a = act.groupby(key, sort=False).agg(actual_fte=("fte", "mean"), actual_cost=("cost", "sum")).reset_index()
    b = bud.groupby(key, sort=False).agg(budget_fte=("fte", "mean"), budget_cost=("cost", "sum")).reset_index()
    v = b.merge(a, on=key)
    v["budget_rate"] = v["budget_cost"] / v["budget_fte"]
    v["actual_rate"] = v["actual_cost"] / v["actual_fte"]
    v["volume"] = (v["actual_fte"] - v["budget_fte"]) * v["budget_rate"]
    v["rate"] = (v["actual_rate"] - v["budget_rate"]) * v["actual_fte"]
    v["variance"] = v["actual_cost"] - v["budget_cost"]

    e = v.groupby("country", sort=False).agg(
        budget_fte=("budget_fte", "sum"), actual_fte=("actual_fte", "sum"),
        budget_cost=("budget_cost", "sum"), actual_cost=("actual_cost", "sum"),
        dept_volume=("volume", "sum"), rate=("rate", "sum")).reset_index()
    e["budget_rate"] = e["budget_cost"] / e["budget_fte"]
    e["volume"] = (e["actual_fte"] - e["budget_fte"]) * e["budget_rate"]
    e["mix"] = e["dept_volume"] - e["volume"]
    e["variance"] = e["actual_cost"] - e["budget_cost"]
    return v, e.drop(columns="dept_volume")


def attrition(r: pd.DataFrame, act: pd.DataFrame) -> pd.DataFrame:
    """FY2026 leavers' FTE over average month-end FTE, per year."""
    left = r[(r["exit_key"] > OPENING) & (r["exit_key"] <= CLOSING)]
    rows = []
    for c, d in cells():
        leavers = left.loc[(left["country"] == c) & (left["department"] == d), "fte"].sum()
        avg = act.loc[(act["country"] == c) & (act["department"] == d), "fte"].mean()
        rows.append({"country": c, "department": d, "leavers": leavers, "avg_fte": avg, "rate": leavers / avg})
    return pd.DataFrame(rows)


def loaded_factor(country: str) -> float:
    """On-costs per euro of base pay, for pay added by remediation (no cap applied)."""
    if country == "IT":
        return 1 + C.IT_IVS + C.IT_OTHER + 1 / C.TFR_DIVISOR
    if country == "PL":
        return (1 + C.PL_PENSION + C.PL_DISABILITY + C.PL_ACCIDENT + C.PL_LABOUR_FUND + C.PL_FGSP
                + C.PL_PPK * C.PPK_PARTICIPATION)
    if country == "DE":
        return 1 + (C.DE_PENSION + C.DE_UNEMPLOYMENT + C.DE_HEALTH + C.DE_HEALTH_EXTRA + C.DE_CARE + C.DE_INSOLVENCY
                    + C.DE_U2 + C.DE_ACCIDENT)
    if country == "ES":
        return 1 + C.ES_COMMON + C.ES_MEI + C.ES_UNEMPLOYMENT + C.ES_FOGASA + C.ES_TRAINING + C.ES_ACCIDENT
    raise ValueError(f"no employer-cost rules for {country}")


def fx_factor(country: str, eur_pln: float) -> float:
    """Polish pay is set in zloty: its euro cost scales with the exchange rate (every Polish rule is in PLN)."""
    return C.EUR_PLN / eur_pln if country == "PL" else 1.0


def renewal(country: str, on: int) -> tuple[float, int]:
    """The entity's collective rise and its first month, or no rise when the scenario leaves renewals off."""
    rise, month = C.RENEWAL[country]
    return (rise, month) if on else (0.0, month)


def forecast(r: pd.DataFrame, act: pd.DataFrame, scenario: tuple) -> tuple[pd.DataFrame, pd.DataFrame]:
    name, att_x, repl, growth_x, freeze_from, rem_from, renew, eur_pln = scenario
    start = opening(r, CLOSING)
    attr = attrition(r, act).set_index(["country", "department"])
    rows = []
    for s in start.itertuples(index=False):
        a = attr.loc[(s.country, s.department), "rate"] * att_x / 12
        g = C.FORECAST_GROWTH[s.department] * growth_x
        fx = fx_factor(s.country, eur_pln)
        rise, rise_from = renewal(s.country, renew)
        fte_prev, leavers_hist = s.fte, []
        for m in range(1, C.MONTHS + 1):
            leavers = fte_prev * a
            backfill_base = leavers_hist[m - 1 - C.TIME_TO_HIRE] if m > C.TIME_TO_HIRE else s.fte * a
            frozen = freeze_from > 0 and m >= freeze_from
            hires = 0.0 if frozen else backfill_base * repl + s.fte * g / 12
            fte = fte_prev - leavers + hires
            rate = (s.rate * fx * (1 + C.MERIT[s.country] * (m >= C.MERIT_MONTH))
                    * (1 + rise * (rise_from > 0 and m >= rise_from)))
            rows.append({"scenario": name, "country": s.country, "department": s.department, "month": m,
                         "leavers": leavers, "hires": hires, "fte": fte, "cost": fte * rate / 12,
                         "hiring_cost": hires * C.COST_PER_HIRE[s.country]})
            leavers_hist.append(leavers)
            fte_prev = fte
    f = pd.DataFrame(rows)
    rem = pd.DataFrame([{"scenario": name, "country": c, "month": m,
                         "remediation": (C.REMEDIATION[c] * loaded_factor(c) * fx_factor(c, eur_pln) / 12
                                         if rem_from > 0 and m >= rem_from else 0.0)}
                        for c in C.ENTITIES for m in range(1, C.MONTHS + 1)])
    return f, rem


def summary(act: pd.DataFrame, forecasts: dict) -> pd.DataFrame:
    """FY2027 total by scenario and entity, with the bridge from FY2026 actuals."""
    rows = []
    for name, (f, rem) in forecasts.items():
        for c in C.ENTITIES:
            a = act[act["country"] == c]
            fy = f[f["country"] == c]
            a_fte = a.groupby("month")["fte"].sum().mean()
            a_cost = a["cost"].sum()
            f_fte = fy.groupby("month")["fte"].sum().mean()
            f_cost = fy["cost"].sum()
            remediation = rem.loc[rem["country"] == c, "remediation"].sum()
            a_rate, f_rate = a_cost / a_fte, f_cost / f_fte
            rows.append({
                "scenario": name, "country": c,
                "fy26_fte": a_fte, "fy26_cost": a_cost,
                "fy27_fte": f_fte, "closing_fte": fy.loc[fy["month"] == C.MONTHS, "fte"].sum(),
                "fy27_payroll": f_cost,
                "fy27_remediation": remediation,
                "fy27_cost": f_cost + remediation,
                "fy27_hires": fy["hires"].sum(),
                "fy27_hiring_cost": fy["hiring_cost"].sum(),
                "bridge_volume": (f_fte - a_fte) * a_rate,
                "bridge_rate": (f_rate - a_rate) * f_fte,
                "bridge_remediation": remediation,
            })
    return pd.DataFrame(rows)


def outlook(r: pd.DataFrame, act: pd.DataFrame, closed: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """FY2027 as it stands after the closed months: actuals for those, then the base case's rules from where the
    year has got to. Attrition is the closed months' (leavers over FTE, a month), cost per FTE the last closed
    month's run-rate, still due the pay review. With no closed months it is the base case."""
    k = int(closed["month"].max()) if len(closed) else 0
    _, att_x, repl, growth_x = C.SCENARIOS[0][:4]
    start = opening(r, CLOSING)
    attr = attrition(r, act).set_index(["country", "department"])
    rows, cells = [], []
    for s in start.itertuples(index=False):
        y = closed[(closed["country"] == s.country) & (closed["department"] == s.department)].set_index("month")
        if k > 0:
            a = y["leavers"].sum() / y["fte"].sum()
            rate0 = y.loc[k, "cost"] * 12 / y.loc[k, "fte"]
        else:
            a = attr.loc[(s.country, s.department), "rate"] * att_x / 12
            rate0 = s.rate
        g = C.FORECAST_GROWTH[s.department] * growth_x
        merit = C.MERIT[s.country]
        cells.append({"country": s.country, "department": s.department, "opening": s.fte, "attrition": a,
                      "rate0": rate0})
        prev, hist = s.fte, []
        for m in range(1, C.MONTHS + 1):
            if m <= k:
                leavers, hires, fte, cost = (y.loc[m, x] for x in ("leavers", "hires", "fte", "cost"))
            else:
                leavers = prev * a
                backfill = hist[m - 1 - C.TIME_TO_HIRE] if m > C.TIME_TO_HIRE else s.fte * a
                hires = backfill * repl + s.fte * g / 12
                fte = prev - leavers + hires
                cost = fte * (rate0 * (1 + merit * (m >= C.MERIT_MONTH)) / (1 + merit * (k >= C.MERIT_MONTH))) / 12
            rows.append({"country": s.country, "department": s.department, "month": m, "actual": m <= k,
                         "leavers": leavers, "hires": hires, "fte": fte, "cost": cost,
                         "hiring_cost": hires * C.COST_PER_HIRE[s.country]})
            hist.append(leavers)
            prev = fte
    return pd.DataFrame(rows), pd.DataFrame(cells)


def plan(out_months: pd.DataFrame, out_cells: pd.DataFrame, k: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The headcount plan: the same steady number of hires each month, from the first month a search started now
    can fill (after the closed months and the time to hire), that lands each cell on its June 2027 target.
    Until then the outlook's hires, already in the pipeline. With attrition a and q = 1 - a, n months from FTE F:
    F x q^n + h x (1 - q^n) / a = target, so h = (target - F x q^n) x a / (1 - q^n); none if the cell
    would close at or above its target without hiring."""
    p = k + C.TIME_TO_HIRE
    n = C.MONTHS - p
    om = out_months.set_index(["country", "department", "month"])
    rows, cells = [], []
    for c in out_cells.itertuples(index=False):
        target = c.opening * (1 + C.PLAN_TARGET[c.department])
        a = c.attrition
        f_p = om.loc[(c.country, c.department, min(p, C.MONTHS)), "fte"] if p > 0 else c.opening
        if n <= 0:
            h = 0.0
        elif a > 0:
            h = max(0.0, (target - f_p * (1 - a) ** n) * a / (1 - (1 - a) ** n))
        else:
            h = max(0.0, (target - f_p) / n)
        merit = C.MERIT[c.country]
        cells.append({"country": c.country, "department": c.department, "target": target, "monthly_hires": h,
                      "first_month": p + 1})
        prev = c.opening
        for m in range(1, C.MONTHS + 1):
            o = om.loc[(c.country, c.department, m)]
            if m <= p:
                leavers, hires, fte, cost = o["leavers"], o["hires"], o["fte"], o["cost"]
            else:
                leavers = prev * a
                hires = h
                fte = prev - leavers + hires
                cost = fte * (c.rate0 * (1 + merit * (m >= C.MERIT_MONTH)) / (1 + merit * (k >= C.MERIT_MONTH))) / 12
            rows.append({"country": c.country, "department": c.department, "month": m, "leavers": leavers,
                         "hires": hires, "fte": fte, "cost": cost, "hiring_cost": hires * C.COST_PER_HIRE[c.country]})
            prev = fte
    return pd.DataFrame(rows), pd.DataFrame(cells)


def outlook_summary(budget27: pd.DataFrame, out_months: pd.DataFrame, plan_months: pd.DataFrame,
                    plan_cells: pd.DataFrame, k: int) -> pd.DataFrame:
    """By entity: the FY2027 budget (the base case approved in June 2026), the outlook and the variance between
    them, split into volume and rate as for FY2026; then what the headcount plan adds to the outlook."""
    rows = []
    for c in C.ENTITIES:
        b, o, pl = (x[x["country"] == c] for x in (budget27, out_months, plan_months))
        b_fte = b.groupby("month")["fte"].sum().mean()
        o_fte = o.groupby("month")["fte"].sum().mean()
        p_fte = pl.groupby("month")["fte"].sum().mean()
        b_cost, o_cost, p_cost = b["cost"].sum(), o["cost"].sum(), pl["cost"].sum()
        b_rate, o_rate = b_cost / b_fte, o_cost / o_fte
        rows.append({
            "country": c, "budget_fte": b_fte, "budget_payroll": b_cost,
            "budget_closing": b.loc[b["month"] == C.MONTHS, "fte"].sum(),
            "budget_hiring_cost": b["hiring_cost"].sum(),
            "ytd_budget": b.loc[b["month"] <= k, "cost"].sum(), "ytd_actual": o.loc[o["month"] <= k, "cost"].sum(),
            "outlook_fte": o_fte, "outlook_payroll": o_cost,
            "outlook_closing": o.loc[o["month"] == C.MONTHS, "fte"].sum(),
            "outlook_hiring_cost": o["hiring_cost"].sum(),
            "variance": o_cost - b_cost, "volume": (o_fte - b_fte) * b_rate, "rate": (o_rate - b_rate) * o_fte,
            "plan_target": plan_cells.loc[plan_cells["country"] == c, "target"].sum(),
            "plan_closing": pl.loc[pl["month"] == C.MONTHS, "fte"].sum(), "plan_fte": p_fte,
            "plan_hires": pl["hires"].sum(), "plan_hiring_cost": pl["hiring_cost"].sum(), "plan_payroll": p_cost,
            "plan_vs_outlook": p_cost - o_cost,
        })
    return pd.DataFrame(rows)


def run(r: pd.DataFrame | None = None) -> dict:
    """The whole model; pass a subset of roster() to run it on a sample."""
    r = roster() if r is None else r.reset_index(drop=True)
    act = actuals(r)
    bud = budget(r)
    var_dept, var_entity = variance(act, bud)
    forecasts = {s[0]: forecast(r, act, s) for s in C.SCENARIOS}
    start = opening(r, CLOSING)
    closed = ytd.actuals(start, attrition(r, act))
    k = int(closed["month"].max()) if len(closed) else 0
    out_months, out_cells = outlook(r, act, closed)
    plan_months, plan_cells = plan(out_months, out_cells, k)
    return {
        "ytd": closed, "outlook": out_months, "outlook_cells": out_cells, "plan": plan_months,
        "plan_cells": plan_cells,
        "outlook_summary": outlook_summary(forecasts[C.SCENARIOS[0][0]][0], out_months, plan_months, plan_cells, k),
        "roster": r, "actuals": act, "budget": bud,
        "variance_dept": var_dept, "variance_entity": var_entity,
        "attrition": attrition(r, act), "start": start,
        "forecasts": forecasts, "summary": summary(act, forecasts),
    }
