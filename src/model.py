"""
The workforce cost model in pandas. Every function has a twin in the Excel workbook built by
build_workbook.py, written with the same order of operations so the two agree.

    roster()      one row per employee of the Italian and Polish entities, with the fully
                  loaded annual cost
    actuals()     FY2026 month-end FTE and cost, by entity and department
    budget()      the FY2026 plan
    variance()    FY2026 actual against budget: volume, mix and rate
    forecast()    FY2027 month by month, for each scenario
"""
import calendar
import hashlib
from datetime import date

import pandas as pd

import config as C

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
    """Everyone employed by the Italian or Polish entity at any point of FY2026."""
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
    it = r["country"] == "IT"
    capped = r["gross"].clip(upper=pl_cap_eur())
    it_social = r["gross"] * C.IT_IVS + r["gross"] * C.IT_OTHER
    pl_social = (capped * C.PL_PENSION + capped * C.PL_DISABILITY + r["gross"] * C.PL_ACCIDENT
                 + r["gross"] * C.PL_LABOUR_FUND + r["gross"] * C.PL_FGSP
                 + r["gross"] * C.PL_PPK * C.PPK_PARTICIPATION)
    r["employer_social"] = it_social.where(it, pl_social)
    r["tfr"] = (r["base"] / C.TFR_DIVISOR).where(it, 0.0)
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
    return (1 + C.PL_PENSION + C.PL_DISABILITY + C.PL_ACCIDENT + C.PL_LABOUR_FUND + C.PL_FGSP
            + C.PL_PPK * C.PPK_PARTICIPATION)


def forecast(r: pd.DataFrame, act: pd.DataFrame, scenario: tuple) -> tuple[pd.DataFrame, pd.DataFrame]:
    name, att_x, repl, growth_x, freeze_from, rem_from = scenario
    start = opening(r, CLOSING)
    attr = attrition(r, act).set_index(["country", "department"])
    rows = []
    for s in start.itertuples(index=False):
        a = attr.loc[(s.country, s.department), "rate"] * att_x / 12
        g = C.FORECAST_GROWTH[s.department] * growth_x
        fte_prev, leavers_hist = s.fte, []
        for m in range(1, C.MONTHS + 1):
            leavers = fte_prev * a
            backfill_base = leavers_hist[m - 1 - C.TIME_TO_HIRE] if m > C.TIME_TO_HIRE else s.fte * a
            frozen = freeze_from > 0 and m >= freeze_from
            hires = 0.0 if frozen else backfill_base * repl + s.fte * g / 12
            fte = fte_prev - leavers + hires
            rate = s.rate * (1 + C.MERIT[s.country] * (m >= C.MERIT_MONTH))
            rows.append({"scenario": name, "country": s.country, "department": s.department, "month": m,
                         "leavers": leavers, "hires": hires, "fte": fte, "cost": fte * rate / 12,
                         "hiring_cost": hires * C.COST_PER_HIRE[s.country]})
            leavers_hist.append(leavers)
            fte_prev = fte
    f = pd.DataFrame(rows)
    rem = pd.DataFrame([{"scenario": name, "country": c, "month": m,
                         "remediation": (C.REMEDIATION[c] * loaded_factor(c) / 12
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


def run(r: pd.DataFrame | None = None) -> dict:
    """The whole model; pass a subset of roster() to run it on a sample."""
    r = roster() if r is None else r.reset_index(drop=True)
    act = actuals(r)
    bud = budget(r)
    var_dept, var_entity = variance(act, bud)
    forecasts = {s[0]: forecast(r, act, s) for s in C.SCENARIOS}
    return {
        "roster": r, "actuals": act, "budget": bud,
        "variance_dept": var_dept, "variance_entity": var_entity,
        "attrition": attrition(r, act), "start": opening(r, CLOSING),
        "forecasts": forecasts, "summary": summary(act, forecasts),
    }
