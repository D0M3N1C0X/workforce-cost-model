<picture>
  <source media="(prefers-color-scheme: dark)" srcset="site-assets/cover-dark.png">
  <img alt="What will next year's people cost be? €192.9M in FY2027's base case, €9.9M over budget in FY2026, 64 hires a month from January to land on the June 2027 headcount plan." src="site-assets/cover-light.png">
</picture>

<p align="center">
  <a href="https://d0m3n1c0x.github.io/workforce-cost-model/simulator/"><b>Try the scenario simulator</b></a> ·
  <a href="https://d0m3n1c0x.github.io/workforce-cost-model/">Read the CFO memo</a> ·
  <a href="https://github.com/D0M3N1C0X/workforce-cost-model/raw/main/deliverables/workforce_cost_model.xlsx">Excel model</a>
</p>

<p align="center">
  <a href="https://github.com/D0M3N1C0X/workforce-cost-model/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/D0M3N1C0X/workforce-cost-model/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-0071e3">
  <img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-6e6e73">
</p>

## Why this matters

People are most of the cost base, and the budget for them is usually a spreadsheet nobody can audit: an
average salary times a headcount, a percentage for "on-costs", and a variance explained after the fact. This model
answers the questions a finance director actually asks, for an employer in **Milan, Kraków, Munich and
Barcelona**, **as HR and finance
would build it together**: what does one person really cost in each country, why did last year's people budget
overrun, what will next year cost if we freeze hiring, lose more people, sign a renewal or start closing pay gaps, and
once the year is under way, where is it heading and how many people do we have to hire to land on plan?

> **Synthetic company, real rules.** The employees are the organisation analysed in
> [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics); the budget, growth plans, pay review,
> renewals, the July-October 2026 actuals and the headcount plan are invented. Italian, Polish, German and Spanish employer costs follow the 2026 rules, ceiling by ceiling,
> each with its source and status in the [verification register](docs/verification.md). Not payroll or tax advice.

## The answer, for the finance director

| | |
|---|---|
| **FY2026 closed €9.9M (5.6%) over budget, at €185.5M**, for 3,311 FTE on average in four countries. Volume explains it: headcount ahead of plan added €10.3M. | **A fully loaded employee costs €74,887 per FTE in Munich, €59,382 in Milan, €53,371 in Barcelona and €41,727 in Kraków.** Ceilings matter: 226 German employees earn above the health and care ceiling, 64 Spanish ones above the maximum base, 79 Polish ones above the ZUS cap. |
| **FY2027 costs €192.9M in the base case (+4.0%)**: more FTE and the January pay review. | **A hiring freeze from October cuts it to €182.6M**, but the year ends with 411 fewer FTE than the base case: a capacity decision, not a finance one. |
| **Higher attrition barely moves payroll** but lifts recruitment cost to €2.49M. | **Closing pay gaps from January 2027 adds €1.23M** to FY2027 and €2.46M a year after, using the gaps found by [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit). |
| **Collective renewals and a stronger zloty add €4.45M**, to €197.3M; the exchange rate alone adds €3.12M to Polish pay set in zloty. | **After October, FY2027 is heading for €193.1M, €0.18M over budget, for the wrong reasons**: 10 fewer FTE than planned save €0.60M, a higher cost per FTE adds €0.77M, most of it in Kraków. |
| **Landing on the June 2027 headcount plan takes 64 hires a month from January** and adds €1.15M to the outlook's payroll. | |

<img alt="Volume explains the FY2026 overrun" src="reports/figures/02_variance_bridge.svg" width="100%">

## Run your own scenarios

The simulator moves the levers a budget meeting argues about (leavers, backfills, growth, a hiring freeze, the pay
review, collective renewals, the zloty, closing pay gaps) and shows FY2027 month by month, the bridge from last year
and the sentence for the CFO, with up to five scenarios side by side. A second view rolls the year forward from the
closed months and turns a headcount target into hires a month. It runs on the sample company or on a client's own staff list, which never
leaves the computer, and it also tells you what one employee costs in Italy, Poland, Germany and Spain, item by item.

<p align="center"><a href="https://d0m3n1c0x.github.io/workforce-cost-model/simulator/"><img alt="The scenario simulator: levers, FY2027 cost, the sentence for the CFO and scenarios compared month by month." src="site-assets/tool.webp" width="100%"></a></p>

## What you get

| Deliverable | For | What is in it |
|---|---|---|
| [`workforce_cost_model.xlsx`](deliverables/workforce_cost_model.xlsx) | the finance team | Twenty sheets: dashboard with a scenario picker, scenario summary and bridge, the FY2027 outlook against budget, FY2026 variance, actuals and budget, FY2027 drivers, one forecast sheet per scenario, the closed months of FY2027, the outlook and the headcount plan month by month, the employee roster, settings and a reconciliation sheet. **Every figure is a live formula**: change a contribution rate, an attrition multiplier or a hiring-freeze month and the model recalculates. |
| [Scenario simulator](https://d0m3n1c0x.github.io/workforce-cost-model/simulator/) | the HR business partner and finance, in the budget meeting | Levers for leavers, backfills, growth, a hiring freeze, the pay review, collective renewals, the zloty and closing pay gaps; FY2027 month by month, the bridge and the sentence for the CFO; up to five scenarios side by side; an Excel download; the outlook after the closed months and the hires a month a headcount target takes. Runs on the sample company or on a client's own staff list, and **the file never leaves the computer**. Also: what one employee costs in Italy, Poland, Germany and Spain, item by item. English and Italian. |
| [`cfo_memo.md`](reports/cfo_memo.md) | the finance director | Answer first: where the FY2026 budget went, what an employee costs in each country, FY2027 under five scenarios, the outlook after October against budget, the headcount plan, seven recommendations, method and limits. |
| [`docs/method.md`](docs/method.md) · [`docs/verification.md`](docs/verification.md) | reviewers | Every formula and simplification; the source and status of every rate and cap. |

## The judgement calls

- **A person's cost is loaded with every employer contribution**, ceiling by ceiling: INPS and TFR in Italy; ZUS with
  its annual 30-times cap, the Labour Fund, FGŚP and PPK in Poland; pension, health and care insurance with their two
  ceilings in Germany; Seguridad Social up to the maximum base, and the solidarity contribution above it, in Spain.
  "Salary plus 30%" is the error this replaces: on-costs run from 21% of gross pay in Kraków and Munich to 37% in Milan.
- **The variance is split into volume, mix and rate**, and the parts add up exactly to the overrun: the finance
  director sees that headcount, not pay, explains last year.
- **Fiscal years run July to June**, so FY2026 ends on the date of the source snapshot, and a month is its month-end
  payroll.
- **The forecast moves FTE, not people**: leavers follow last year's attrition, 90% are replaced after two months,
  planned growth comes on top.
- **Recruitment cost is kept apart from payroll**, so higher attrition shows its real price instead of looking like a
  saving.
- **Closing pay gaps is priced with on-costs**, from the gaps found by the
  [pay transparency kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit), and starts before the first
  reports are due.
- **Polish pay is priced in zloty**: a stronger zloty raises its euro cost, ceilings included, because every Polish
  rule is set in PLN.
- **The outlook rolls forward from what happened**: the closed months' attrition and the last month's cost per FTE,
  not the plan's, and the variance against budget splits into volume and rate like last year's.
- **A headcount target becomes hires a month**: the same number each month once a search opened today can fill a post,
  enough to offset leavers and land on the target, solved in closed form so the workbook can show it as one formula.

Every formula and simplification is in [docs/method.md](docs/method.md).

## Built to be checked

| | |
|---|---|
| **Three engines, one answer** | pandas, the Excel model's live formulas (reconciled on 1649 checks, recalculated in CI by LibreOffice) and the browser simulator (checked against the model on 43,152 values) |
| **Every rate sourced** | a [verification register](docs/verification.md) with the source, its status and the date each rate and ceiling was read |
| **A client-ready workbook** | inputs in blue, formulas in black, key assumptions in yellow, one Settings sheet, a scenario picker, no dynamic arrays |
| **Reproducible** | one command rebuilds every output; CI fails if a rebuilt file differs from the committed one |

<details>
<summary><b>For engineers: how it fits together, how to run it</b></summary>

```mermaid
flowchart LR
    A[hr-people-analytics<br/>employees.csv] --> R[model.py<br/>roster + loaded cost]
    S[config.py<br/>2026 rates, budget, scenarios] --> R
    K[pay-transparency-readiness-kit<br/>remediation cost] --> S
    R --> V[FY2026<br/>actuals, budget, variance]
    R --> F[FY2027<br/>forecast x 5 scenarios]
    Y[ytd.py<br/>closed months, synthetic] --> O[FY2027 outlook<br/>+ headcount plan]
    R --> O
    V & F & O --> X[Excel model<br/>live formulas]
    V & F & O --> M[CFO memo + figures]
    X --> C{check_workbook.py<br/>formulas = pandas?}
```

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py        # a few seconds
pip install -r requirements-dev.txt
pytest                       # includes a sample workbook calculated in pure Python
node tests/js/check_engine.mjs   # the simulator against the model
```

The reconciliation check, the LibreOffice recalculation and the byte-stable workbook come from
[excel-twin](https://github.com/D0M3N1C0X/excel-twin), a small library shared by the portfolio.

```
├── data/source/employees.csv    the organisation from hr-people-analytics (checksum pinned)
├── src/
│   ├── config.py                every rate, cap and assumption, with its source
│   ├── model.py                 roster, actuals, budget, variance, forecast, bridge, outlook, plan
│   ├── ytd.py                   the closed months of FY2027 (synthetic)
│   ├── build_workbook.py        the Excel model and its reconciliation sheet
│   ├── check_workbook.py        proves the formulas reproduce pandas
│   ├── recalc_libreoffice.py    recalculates the workbook headless, for CI
│   ├── build_memo.py            the memo and its figures
│   ├── charts.py                five SVG charts in the portfolio identity, light and dark
│   ├── report_html.py           the memo as one HTML page
│   ├── deterministic.py         byte-stable Office files
│   └── run_all.py               the whole pipeline
├── deliverables/                the workbook
├── reports/                     the memo, its HTML page and figures
├── docs/                        method and verification register
└── tests/
```

</details>

## About

Built by **Domenico Perroni**: HR advisory for the Italian market, people analytics and reward, based in Kraków.
[GitHub](https://github.com/D0M3N1C0X) · [LinkedIn](https://www.linkedin.com/in/domenico-perroni) · [Portfolio](https://d0m3n1c0x.github.io/)

**More from the same portfolio**

- [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit) — the EU Pay Transparency Directive run end to end on the same organisation: a live Excel model reconciled with pandas, a board briefing and a readiness checklist, with the [report online](https://d0m3n1c0x.github.io/pay-transparency-readiness-kit/); its remediation cost feeds this model
- [equal-value-pay-ranges](https://github.com/D0M3N1C0X/equal-value-pay-ranges) — from family pay bands to one range per grade and country for the same organisation: Eurostat market pricing for four countries, a live Excel model reconciled with pandas, and a [pay range finder](https://d0m3n1c0x.github.io/equal-value-pay-ranges/ads.html) for job ads
- [controlli-cedolini](https://github.com/D0M3N1C0X/controlli-cedolini) — the Italian payroll side in practice: fourteen checks on monthly payslips under the CCNL Terziario, terminations included, in Python, a Google Sheets-ready workbook and a browser tool, with the cost of the November 2026 pay increase; the tool in English and Italian
- [where-pay-transparency-bites](https://github.com/D0M3N1C0X/where-pay-transparency-bites) — Eurostat data for all 27 Member States, analysed in R: the published gender pay gap understates the gap inside sectors; [article](https://d0m3n1c0x.github.io/where-pay-transparency-bites/), [dashboard](https://d0m3n1c0x.github.io/where-pay-transparency-bites/dashboard/) and [working paper](https://d0m3n1c0x.github.io/where-pay-transparency-bites/paper.pdf)
- [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics) — attrition drivers, EU pay-transparency exposure and HR service-desk performance on the synthetic 4,000-employee organisation used here, with the [report online](https://d0m3n1c0x.github.io/hr-people-analytics/)
- [engagement-survey-analytics](https://github.com/D0M3N1C0X/engagement-survey-analytics) — an employee engagement survey analysed end to end, with a [live dashboard](https://d0m3n1c0x.github.io/engagement-survey-analytics/) you can filter in the browser
- [job-search-agent](https://github.com/D0M3N1C0X/job-search-agent) — a job search run as a pipeline: public ATS board APIs, explainable fit scoring, funnel analytics
- [pompei-stratificata](https://github.com/D0M3N1C0X/pompei-stratificata) — Pompeii and Herculaneum from AD 79 to today, a [walkable model](https://d0m3n1c0x.github.io/pompei-stratificata/) with a sourced documentary dossier, in six languages

MIT licensed. Reuse anything here.
