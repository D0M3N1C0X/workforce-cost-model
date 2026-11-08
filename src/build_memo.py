"""
Writes reports/cfo_memo.md and its figures: the read-out a finance director would get.
Every figure comes from model.run(), the same results the workbook reconciles against.
"""
import pandas as pd

import charts
import config as C
import model

FIG = C.REPORTS / "figures"
SCEN_SHOWN = ["Base", "Hiring freeze", "High attrition"]


def m(x, d=1):
    return f"{'−' if round(x / 1e6, d) < 0 else ''}€{abs(x) / 1e6:,.{d}f}M"


def ms(x, d=2):
    """Money with its sign, for a change."""
    return ("+" if round(x / 1e6, d) > 0 else "") + m(x, d)


def k(x):
    return f"{'−' if x < 0 else ''}€{abs(x) / 1e3:,.0f}k"


def pct(x, d=1):
    return f"{'−' if x < 0 else ''}{abs(x) * 100:.{d}f}%"


def signed(x, d=1):
    return f"{'+' if x >= 0 else '−'}{abs(x) * 100:.{d}f}%"


def listing(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def table(head, rows, align):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---:" if a == "r" else "---" for a in align) + "|"]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def month_label(ts):
    return ts.strftime("%b %y")


def facts(o: dict) -> dict:
    ve = o["variance_entity"].set_index("country")
    s = o["summary"]
    tot = s.groupby("scenario", sort=False)[["fy26_cost", "fy27_cost", "fy27_payroll", "fy27_remediation",
                                              "fy27_hires", "fy27_hiring_cost", "closing_fte", "fy27_fte",
                                              "fy26_fte"]].sum()
    r = o["roster"]
    base, freeze, high, equity, cost = (tot.loc[n] for n in ("Base", "Hiring freeze", "High attrition",
                                                              "Pay equity first", "Cost pressure"))
    by = s.set_index(["scenario", "country"])
    osum = o["outlook_summary"].set_index("country")
    k_closed = int(o["ytd"]["month"].max()) if len(o["ytd"]) else 0
    return {"ve": ve, "tot": tot, "base": base, "freeze": freeze, "high": high, "equity": equity, "cost": cost,
            "fx_pl": by.loc[("Cost pressure", "PL"), "fy27_cost"] - by.loc[("Base", "PL"), "fy27_cost"],
            "os": osum, "os_all": osum.sum(numeric_only=True), "k": k_closed, "plan_cells": o["plan_cells"],
            "fte_gap": osum["budget_fte"].sum() - osum["outlook_fte"].sum(),
            "plan_monthly": o["plan_cells"]["monthly_hires"].sum(),
            "plan_first": int(o["plan_cells"]["first_month"].iloc[0]),
            "above_cap": int(((r["country"] == "PL") & (r["gross"] > model.pl_cap_eur())).sum()),
            "pl_n": int((r["country"] == "PL").sum()),
            "de_above": int(((r["country"] == "DE") & (r["gross"] > C.DE_CAP_HEALTH)).sum()),
            "de_n": int((r["country"] == "DE").sum()),
            "es_above": int(((r["country"] == "ES") & (r["gross"] > C.ES_CAP)).sum()),
            "es_n": int((r["country"] == "ES").sum()),
            "attr": o["attrition"].groupby("country").apply(lambda g: g["leavers"].sum() / g["avg_fte"].sum()),
            "attr_all": o["attrition"]["leavers"].sum() / o["attrition"]["avg_fte"].sum()}


def write(o: dict) -> dict:
    f = facts(o)
    ve, tot, base, freeze, high, equity = (f[x] for x in ("ve", "tot", "base", "freeze", "high", "equity"))
    FIG.mkdir(parents=True, exist_ok=True)
    act, bud = o["actuals"], o["budget"]
    months26 = [month_label(t) for t in model.FY26]
    months27 = [month_label(t) for t in model.month_ends(C.FY2027_START)]
    a_fte = act.groupby("month")["fte"].sum().tolist()
    b_fte = bud.groupby("month")["fte"].sum().tolist()
    over = sum(a_fte) / 12 - sum(b_fte) / 12
    (FIG / "01_fte_budget_actual.svg").write_text(charts.fte_budget_actual(
        months26, b_fte, a_fte, f"Headcount ran {over:,.0f} FTE ahead of plan on average"))
    bridge_rows = [(C.ENTITIES[c], ve.loc[c, "budget_cost"], ve.loc[c, "volume"], ve.loc[c, "mix"],
                    ve.loc[c, "rate"], ve.loc[c, "actual_cost"]) for c in C.ENTITIES]
    (FIG / "02_variance_bridge.svg").write_text(charts.variance_bridge(
        bridge_rows, "Volume explains the FY2026 overrun"))
    rows = [(n, tot.loc[n, "fy27_cost"], tot.loc[n, "fy27_hiring_cost"]) for n in tot.index]
    (FIG / "03_scenario_costs.svg").write_text(charts.scenario_costs(
        rows, base["fy26_cost"], "FY2027 people cost ranges from "
        f"{m(min(r[1] for r in rows))} to {m(max(r[1] for r in rows))}"))
    paths = {}
    for n in SCEN_SHOWN:
        fc, _ = o["forecasts"][n]
        paths[n] = fc.groupby("month")["fte"].sum().tolist()
    (FIG / "04_fte_paths.svg").write_text(charts.fte_paths(
        months26 + months27, a_fte, paths, "A hiring freeze ends the year with far fewer people"))
    osum, os_all = f["os"], f["os_all"]
    closed_to = model.month_ends(C.FY2027_START)[f["k"] - 1] if f["k"] else None
    (FIG / "05_outlook_bridge.svg").write_text(charts.variance_bridge(
        [(C.ENTITIES[c], osum.loc[c, "budget_payroll"], osum.loc[c, "volume"], osum.loc[c, "rate"],
          osum.loc[c, "outlook_payroll"]) for c in C.ENTITIES],
        "FY2027 outlook: fewer people, each costing more",
        subtitle=(f"FY2027 payroll, outlook after {closed_to:%B %Y} against budget, by effect" if closed_to
                  else "FY2027 payroll, outlook against budget, by effect"),
        labels=("Volume", "Rate"), ends=("Budget", "outlook")))

    vd = o["variance_dept"]
    top = vd.sort_values("variance", ascending=False).head(5)
    r = o["roster"]
    snapshot = r[model.active(r, model.CLOSING)]

    def oncost(g):
        gross = g["gross"].sum()
        return g["employer_social"].sum() / gross, g["tfr"].sum() / gross, g["loaded_cost"].sum() / g["fte"].sum()

    on = {c: oncost(snapshot[snapshot["country"] == c]) for c in C.ENTITIES}
    names = {"IT": "Italy", "PL": "Poland", "DE": "Germany", "ES": "Spain"}
    fy26_total = base["fy26_cost"]
    budget_total = ve["budget_cost"].sum()
    var_total = ve["variance"].sum()
    att_x = next(sc[1] for sc in C.SCENARIOS if sc[0] == "High attrition")
    extra_points = f["attr_all"] * (att_x - 1) * 100
    hiring_per_point = (high["fy27_hiring_cost"] - base["fy27_hiring_cost"]) / extra_points
    fy27_months = model.month_ends(C.FY2027_START)
    freeze_from = next(sc[4] for sc in C.SCENARIOS if sc[0] == "Hiring freeze")
    equity_from = next(sc[5] for sc in C.SCENARIOS if sc[0] == "Pay equity first")
    growing = [d for d in C.DEPARTMENTS if C.FORECAST_GROWTH[d] > 0]
    sb = o["summary"]
    base_bridge = sb[sb["scenario"] == "Base"][["bridge_volume", "bridge_rate"]].sum()
    fb, _ = o["forecasts"]["Base"]
    start_rate = o["start"].set_index(["country", "department"])["rate"]
    merit = sum(row.fte * start_rate[(row.country, row.department)] * C.MERIT[row.country] / 12
                for row in fb[fb["month"] >= C.MERIT_MONTH].itertuples())
    full_year_equity = sum(C.REMEDIATION[c] * model.loaded_factor(c) for c in C.ENTITIES)

    L = []
    add = L.append
    add("# FY2027 people cost: Italy, Poland, Germany and Spain")
    add("")
    add(f"**Scope:** {listing(C.ENTITIES.values())}, {round(base['fy26_fte']):,} FTE on average in FY2026")
    words = {4: "four", 5: "five", 6: "six"}
    add("**Model:** fully loaded cost per employee, FY2026 budget against actual, FY2027 month by month under "
        f"{words.get(len(C.SCENARIOS), len(C.SCENARIOS))} scenarios, the outlook after {closed_to:%B} and a headcount "
        "plan, in a live Excel model reconciled with pandas")
    add("**Data:** synthetic, the organisation analysed in "
        "[hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics); rates and caps for 2026 from "
        "the sources in [docs/verification.md](../docs/verification.md)")
    add("")
    add("> Fiscal years run July to June. The budget, growth plans, pay review, renewals, cost per hire, the "
        f"July-{closed_to:%B} 2026 actuals and the headcount plan are invented for the demonstration; the "
        "employer-cost rules are real and dated.")
    add("")
    add("## The answer")
    add("")
    add(f"- **FY2026 closed {m(var_total)} ({pct(var_total / budget_total)}) over budget, at {m(fy26_total)}.** "
        f"Headcount ran ahead of plan: volume added {m(ve['volume'].sum())}, the department mix "
        f"{m(ve['mix'].sum(), 2)}, while cheaper joiners saved {m(-ve['rate'].sum(), 2)}.")
    review = (f"the {fy27_months[C.MERIT_MONTH - 1]:%B} pay review ("
              + listing(f"{pct(C.MERIT[c])} in {names[c]}" for c in C.ENTITIES) + ")")
    rate_story = ((f"where {review} adds {m(merit)} and the lower cost per FTE of the June 2026 workforce "
                  f"takes back {m(merit - base_bridge['bridge_rate'])}")
                  if merit > base_bridge["bridge_rate"] else f"mostly {review}")
    add(f"- **FY2027 costs {m(base['fy27_cost'])} in the base case ({signed(base['fy27_cost'] / fy26_total - 1)}).** "
        f"More FTE add {m(base_bridge['bridge_volume'])}: the year opens with the headcount FY2026 closed on, and "
        f"{listing(growing)} keep growing. Cost per FTE adds {m(base_bridge['bridge_rate'])}, {rate_story}.")
    add(f"- **A hiring freeze from {fy27_months[freeze_from - 1]:%B} would cut FY2027 to {m(freeze['fy27_cost'])}** "
        f"({signed(freeze['fy27_cost'] / fy26_total - 1)}), but the year would close with "
        f"{base['closing_fte'] - freeze['closing_fte']:,.0f} fewer FTE than the base case: a capacity decision, "
        f"not a finance one.")
    add(f"- **Higher attrition barely moves payroll but costs in hiring.** With attrition {pct(att_x - 1, 0)} higher "
        f"({extra_points:.1f} points), vacancies "
        f"offset the backfills, while recruitment rises to {m(high['fy27_hiring_cost'], 2)} "
        f"({m(high['fy27_hiring_cost'] - base['fy27_hiring_cost'], 2)} more).")
    add(f"- **Starting to close pay gaps in {fy27_months[equity_from - 1]:%B %Y}, before the first pay-transparency "
        f"reports are due, adds {m(equity['fy27_remediation'], 2)} to FY2027** and {m(full_year_equity, 2)} in every full year after, loaded with employer "
        f"costs. The gaps come from "
        f"[pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit).")
    cp = next(sc for sc in C.SCENARIOS if sc[0] == "Cost pressure")
    renewals = listing(f"{pct(C.RENEWAL[c][0])} in {names[c]} from {fy27_months[C.RENEWAL[c][1] - 1]:%B}"
                       for c in C.ENTITIES if C.RENEWAL[c][0])
    add(f"- **Collective renewals and a stronger zloty would add {m(f['cost']['fy27_cost'] - base['fy27_cost'], 2)}**, "
        f"to {m(f['cost']['fy27_cost'])}: renewals of {renewals}, and {cp[7]:.2f} zloty to the euro instead of "
        f"{C.EUR_PLN}, which alone adds {m(f['fx_pl'], 2)} to Polish pay set in zloty.")
    add(f"- **After {closed_to:%B}, FY2027 is heading for {m(os_all['outlook_payroll'])}, "
        f"{m(os_all['variance'], 2)} {'over' if os_all['variance'] > 0 else 'under'} budget, for the wrong reasons.** "
        f"{f['fte_gap']:,.0f} fewer FTE than planned on average save {m(-os_all['volume'], 2)}; a higher cost per "
        f"FTE adds {m(os_all['rate'], 2)}, {pct(osum.loc['PL', 'rate'] / os_all['rate'], 0)} of it in Kraków. "
        f"More leavers also lift recruitment to {m(os_all['outlook_hiring_cost'], 2)} "
        f"({m(os_all['outlook_hiring_cost'] - os_all['budget_hiring_cost'], 2)} over budget).")
    add(f"- **Landing on the June 2027 headcount plan, {os_all['plan_target']:,.0f} FTE, takes "
        f"{f['plan_monthly']:,.0f} hires a month from {fy27_months[f['plan_first'] - 1]:%B}** and adds "
        f"{m(os_all['plan_vs_outlook'], 2)} to the outlook's payroll: searches for those posts have to open now.")
    add("")

    add("## 1. FY2026: where the budget went")
    add("")
    add("![Budget and actual FTE](figures/01_fte_budget_actual.svg)")
    add("")
    add("![Variance bridge](figures/02_variance_bridge.svg)")
    add("")
    add(table(["Employer", "Budget", "Actual", "Volume", "Mix", "Rate", "Variance"],
              [[C.ENTITIES[c], m(e.budget_cost), m(e.actual_cost), m(e.volume, 2), m(e.mix, 2), m(e.rate, 2),
                f"{m(e.variance, 2)} ({pct(e.variance / e.budget_cost)})"]
               for c, e in ve.iterrows()], "lrrrrrr"))
    add("")
    add("*Volume: FTE above plan at budget cost per FTE. Mix: departments with higher cost per FTE grew more. "
        "Rate: actual against budget cost per FTE, at actual FTE.*")
    add("")
    add("The five largest overruns by department:")
    add("")
    add(table(["Employer", "Department", "Budget FTE", "Actual FTE", "Variance", "of which volume"],
              [[C.ENTITIES[t.country], t.department, f"{t.budget_fte:,.0f}", f"{t.actual_fte:,.0f}",
                k(t.variance), k(t.volume)] for t in top.itertuples()], "llrrrr"))
    add("")
    above = int((vd["actual_fte"] > vd["budget_fte"]).sum())
    leaders = top.head(3)
    share = f"All {len(vd)}" if above == len(vd) else f"{above} of {len(vd)}"
    add(f"{share} departments ran above planned FTE. The largest overruns were in "
        + listing(f"{t.department} ({C.ENTITIES[t.country]})" for t in leaders.itertuples())
        + ", where extra headcount met a high cost per FTE.")
    add("")

    add("## 2. What a fully loaded employee costs")
    add("")
    rules = {
        "IT": (f"INPS pension {pct(C.IT_IVS, 2)}, other INPS and INAIL {pct(C.IT_OTHER)} (illustrative), "
               f"TFR at base pay / {C.TFR_DIVISOR}"),
        "PL": (f"ZUS pension {pct(C.PL_PENSION, 2)} and disability {pct(C.PL_DISABILITY, 2)} up to the annual cap; "
               f"accident {pct(C.PL_ACCIDENT, 2)}, Labour Fund {pct(C.PL_LABOUR_FUND, 2)}, FGŚP "
               f"{pct(C.PL_FGSP, 2)}, PPK {pct(C.PL_PPK, 1)} on {pct(C.PPK_PARTICIPATION, 0)} of pay"),
        "DE": (f"pension and unemployment {pct(C.DE_PENSION + C.DE_UNEMPLOYMENT, 1)} up to €{C.DE_CAP_PENSION:,}; "
               f"health, additional contribution and care {pct(C.DE_HEALTH + C.DE_HEALTH_EXTRA + C.DE_CARE, 2)} "
               f"up to €{C.DE_CAP_HEALTH:,}; levies {pct(C.DE_INSOLVENCY + C.DE_U2, 2)}, accident "
               f"{pct(C.DE_ACCIDENT, 2)} (illustrative)"),
        "ES": (f"common contingencies and MEI {pct(C.ES_COMMON + C.ES_MEI, 2)}, unemployment, FOGASA and training "
               f"{pct(C.ES_UNEMPLOYMENT + C.ES_FOGASA + C.ES_TRAINING, 1)}, AT/EP {pct(C.ES_ACCIDENT, 1)}, up to "
               f"€{C.ES_CAP:,.0f}; solidarity contribution above it"),
    }
    add(table(["Employer", "Cost per FTE, June 2026", "Employer social contributions", "TFR", "Contribution rules"],
              [[C.ENTITIES[c], f"€{on[c][2]:,.0f}", f"{pct(on[c][0])} of gross pay",
                f"{pct(on[c][1])} of gross pay" if c == "IT" else "-", rules[c]] for c in C.ENTITIES],
              "lrrrl"))
    add("")
    add(f"*Gross pay is base pay at contracted FTE plus target bonus. In Poland, {f['above_cap']} of "
        f"{f['pl_n']:,} employees earn above the 2026 cap of {C.PL_CAP_PLN:,} PLN "
        f"(€{model.pl_cap_eur():,.0f} at {C.EUR_PLN} PLN per euro), so their pension and disability contributions stop "
        f"part-way through the year. Ceilings bite harder elsewhere: {f['de_above']} of {f['de_n']:,} German employees "
        f"earn above the health and care ceiling, and {f['es_above']} of {f['es_n']:,} Spanish ones above the maximum "
        f"base, where the solidarity contribution takes over at a much lower rate.*")
    add("")

    add(f"## 3. FY2027 under {words.get(len(C.SCENARIOS), len(C.SCENARIOS))} scenarios")
    add("")
    add("![Scenario costs](figures/03_scenario_costs.svg)")
    add("")
    add(table(["Scenario", "People cost", "Change vs FY2026", "Average FTE", "Closing FTE", "Hires",
               "Hiring cost", "Remediation"],
              [[n, m(t.fy27_cost), signed(t.fy27_cost / t.fy26_cost - 1), f"{t.fy27_fte:,.0f}",
                f"{t.closing_fte:,.0f}", f"{t.fy27_hires:,.0f}", m(t.fy27_hiring_cost, 2),
                m(t.fy27_remediation, 2) if t.fy27_remediation else "-"] for n, t in tot.iterrows()],
              "lrrrrrrr"))
    add("")
    add("*People cost = payroll plus pay-equity remediation; hiring cost is shown apart. Scenario settings: "
        + "; ".join(f"{s[0]} - attrition x{s[1]}, replacement {pct(s[2], 0)}, growth x{s[3]}"
                    + (f", freeze from month {s[4]}" if s[4] else "")
                    + (f", remediation from month {s[5]}" if s[5] else "")
                    + (", collective renewals" if s[6] else "")
                    + (f", {s[7]:.2f} PLN per euro" if s[7] != C.EUR_PLN else "") for s in C.SCENARIOS) + ".*")
    add("")
    add("![FTE paths](figures/04_fte_paths.svg)")
    add("")
    add("FY2026 attrition was " + listing(f"{pct(f['attr'][c])} in {names[c]}" for c in C.ENTITIES) + ". The forecast "
        f"backfills {pct(C.SCENARIOS[0][2], 0)} of leavers after {C.TIME_TO_HIRE} months, so each extra point of "
        f"attrition adds about {k(hiring_per_point)} of recruitment cost at the assumed cost per hire.")
    add("")

    add(f"## 4. FY2027 after {closed_to:%B}: outlook against budget")
    add("")
    add("![Outlook against budget](figures/05_outlook_bridge.svg)")
    add("")
    add(table(["Employer", "Budget", f"July-{closed_to:%B}: actual against budget", "Outlook", "Variance", "Volume",
               "Rate", "Hiring cost, outlook (against budget)"],
              [[C.ENTITIES[c], m(v.budget_payroll), ms(v.ytd_actual - v.ytd_budget), m(v.outlook_payroll),
                f"{ms(v.variance)} ({signed(v.variance / v.budget_payroll)})", ms(v.volume), ms(v.rate),
                f"{m(v.outlook_hiring_cost, 2)} ({ms(v.outlook_hiring_cost - v.budget_hiring_cost)})"]
               for c, v in osum.iterrows()], "lrrrrrrr"))
    add("")
    add(f"*Budget: the base case approved in June 2026. Outlook: actuals to {closed_to:%B}, then the base case's "
        "rules from where the year has got to, with the closed months' attrition and the last month's cost per FTE "
        f"(4+8). The {f['k']} closed months are synthetic: Customer Service losing "
        f"{pct(C.YTD_ATTRITION_X['Customer Service'] - 1, 0)} more people than in FY2026, Tech hiring "
        f"{pct(C.YTD_GROWTH_FILL['Tech'], 0)} of its planned growth, pay in Kraków drifting "
        f"{pct(C.YTD_PAY_DRIFT['PL'])} above June. The variance splits like FY2026's: volume at budget cost per FTE, "
        "rate at outlook FTE.*")
    add("")

    add("## 5. The headcount plan")
    add("")
    pcells = f["plan_cells"]
    add(table(["Employer", "Target, June 2027", "Outlook, June 2027", "Plan hires a month", "Hires in FY2027",
               "Hiring cost", "Payroll against outlook"],
              [[C.ENTITIES[c], f"{v.plan_target:,.0f}", f"{v.outlook_closing:,.0f}",
                f"{pcells.loc[pcells['country'] == c, 'monthly_hires'].sum():,.1f}", f"{v.plan_hires:,.0f}",
                m(v.plan_hiring_cost, 2), ms(v.plan_vs_outlook)] for c, v in osum.iterrows()], "lrrrrrr"))
    add("")
    biggest = pcells.sort_values("monthly_hires", ascending=False).head(3)
    add(f"*Targets against June 2026: "
        + listing(f"{d} {signed(g, 0)}" for d, g in C.PLAN_TARGET.items() if g) + ", the rest flat (illustrative). "
        f"Searches opened after the {closed_to:%B} close fill posts {C.TIME_TO_HIRE} months later; until then the "
        "outlook's backfills arrive. From then, the same hires each month: (target - FTE × q^n) × a / (1 - q^n), "
        "with a the monthly attrition, q = 1 - a and n the months left. The largest asks: "
        + listing(f"{t.department} in {names[t.country]}, {t.monthly_hires:.1f} a month" for t in biggest.itertuples())
        + ".*")
    add("")

    add("## 6. Recommendations")
    add("")
    add(f"1. **Set the FY2027 budget at the base case plus pay-equity remediation, {m(equity['fy27_cost'])}.** "
        "The first pay-transparency reports cover 2026 pay and are due in June 2027; gaps that are neither "
        "justified nor closed within six months lead to a joint pay assessment.")
    gap_month = next(i for i, (a, b) in enumerate(zip(a_fte, b_fte)) if a > b * 1.02)
    add(f"2. **Control headcount by position, month by month.** The FY2026 overrun was volume, and actual FTE "
        f"was already more than 2% above plan by {model.FY26[gap_month]:%B %Y}.")
    add("3. **Treat a hiring freeze as an operating decision.** It saves money only by ending the year "
        f"{base['closing_fte'] - freeze['closing_fte']:,.0f} FTE short.")
    add("4. **Price attrition in the budget.** Recruitment cost rises with every leaver, even when payroll does not.")
    add("5. **Replace the illustrative rates with the payroll provider's:** other INPS contributions and INAIL, "
        "the Polish accident rate, PPK participation, the German insurer's additional contribution and accident "
        "rate, the Spanish AT/EP tariff, and cost per hire.")
    add(f"6. **Re-forecast every month from the run-rate.** After {closed_to:%B} the year is close to budget only "
        "because vacancies hide a rising cost per FTE; Kraków's pay drift needs an answer before the January review.")
    add(f"7. **Open the plan's searches now.** A post opened after the {closed_to:%B} close is filled in "
        f"{fy27_months[f['plan_first'] - 1]:%B} at the earliest.")
    add("")

    add("## 7. Method and limits")
    add("")
    add("- **Two engines, one answer.** Every figure is computed in pandas and again by live formulas in "
        "[the workbook](../deliverables/workforce_cost_model.xlsx); its Reconciliation sheet checks each pair, and "
        "CI recalculates the workbook with LibreOffice.")
    add("- **Month-end population.** FTE and cost are counted on the payroll at each month end, from hire and exit "
        "dates.")
    add("- **Simplifications, stated.** Salaries as at 30 June 2026 apply to every month; bonus is paid at target; "
        "TFR accrues on base pay; one cap and one exchange rate apply to the whole year; overtime, leave and "
        "benefits in kind are not modelled. Full list in [docs/method.md](../docs/method.md).")
    add(f"- **Closed months are synthetic.** The July-{closed_to:%B} actuals are written by `src/ytd.py` from the "
        "June 2026 population with drivers that depart from the plan on purpose; they show the method, not a fact.")
    add("- **Not payroll or tax advice.** Rates and caps carry their source and status in "
        "[docs/verification.md](../docs/verification.md).")
    add("")
    (C.REPORTS / "cfo_memo.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return f


def main() -> None:
    write(model.run())
    import report_html
    report_html.build()
    print("memo -> reports/cfo_memo.md, reports/index.html, 5 figures")


if __name__ == "__main__":
    main()
