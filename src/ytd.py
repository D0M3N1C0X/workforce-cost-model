"""
SYNTHETIC actuals for the first months of FY2027 (July to October 2026), the input of the 4+8 outlook.

There is no real payroll behind them. They are written from the population at 30 June 2026 with drivers that
differ from the plan on purpose (config.YTD_*): more leavers in Customer Service, Tech hiring at half the planned
pace, pay drifting up in Kraków. Each figure is then rounded as a payroll extract would be: FTE to one decimal,
cost to the cent. The workbook and the simulator receive them as values, like any month that has closed.
"""
import pandas as pd

import config as C


def actuals(start: pd.DataFrame, attr: pd.DataFrame, months: int = C.YTD_MONTHS) -> pd.DataFrame:
    """Month-end FTE, leavers, hires and cost for the closed months, by entity and department."""
    rates = attr.set_index(["country", "department"])["rate"]
    replacement = C.SCENARIOS[0][2]
    rows = []
    for s in start.itertuples(index=False):
        a = rates[(s.country, s.department)] * C.YTD_ATTRITION_X[s.department] / 12
        g = C.FORECAST_GROWTH[s.department] * C.YTD_GROWTH_FILL[s.department]
        prev, hist = s.fte, []
        for m in range(1, months + 1):
            leavers = round(prev * a, 1)
            backfill = hist[m - 1 - C.TIME_TO_HIRE] if m > C.TIME_TO_HIRE else round(s.fte * a, 1)
            hires = round(backfill * replacement + s.fte * g / 12, 1)
            fte = round(prev - leavers + hires, 1)
            rows.append({"country": s.country, "department": s.department, "month": m, "fte": fte,
                         "leavers": leavers, "hires": hires,
                         "cost": round(fte * s.rate * (1 + C.YTD_PAY_DRIFT[s.country]) / 12, 2)})
            hist.append(leavers)
            prev = fte
    return pd.DataFrame(rows, columns=["country", "department", "month", "fte", "leavers", "hires", "cost"])
