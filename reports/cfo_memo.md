# FY2027 people cost: Italy and Poland

**Scope:** IT · Milan and PL · Kraków, 2,128 FTE on average in FY2026
**Model:** fully loaded cost per employee, FY2026 budget against actual, FY2027 month by month under four scenarios, in a live Excel model reconciled with pandas
**Data:** synthetic, the organisation analysed in [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics); rates and caps for 2026 from the sources in [docs/verification.md](../docs/verification.md)

> Fiscal years run July to June. The budget, growth plans, pay review and cost per hire are invented for the demonstration; the employer-cost rules are real and dated.

## The answer

- **FY2026 closed €5.8M (5.7%) over budget, at €107.1M.** Headcount ran ahead of plan: volume added €6.3M, the department mix €0.18M, while cheaper joiners saved €0.68M.
- **FY2027 costs €111.0M in the base case (+3.6%).** More FTE add €2.2M: the year opens with the headcount FY2026 closed on, and Customer Service, Tech and Sales keep growing. Cost per FTE adds €1.7M, where the January pay review (2.5% in Italy, 5.0% in Poland) adds €2.0M and the lower cost per FTE of the June 2026 workforce takes back €0.3M.
- **A hiring freeze from October would cut FY2027 to €104.6M** (−2.3%), but the year would close with 278 fewer FTE than the base case: a capacity decision, not a finance one.
- **Higher attrition barely moves payroll but costs in hiring.** With attrition 30% higher (5.3 points), vacancies offset the backfills, while recruitment rises to €1.54M (€0.33M more).
- **Starting to close pay gaps in January 2027, before the first pay-transparency reports are due, adds €0.76M to FY2027** and €1.52M in every full year after, loaded with employer costs. The gaps come from [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit).

## 1. FY2026: where the budget went

![Budget and actual FTE](figures/01_fte_budget_actual.svg)

![Variance bridge](figures/02_variance_bridge.svg)

| Employer | Budget | Actual | Volume | Mix | Rate | Variance |
|---|---:|---:|---:|---:|---:|---:|
| IT · Milan | €57.7M | €60.8M | €3.51M | €0.06M | −€0.51M | €3.06M (5.3%) |
| PL · Kraków | €43.6M | €46.3M | €2.79M | €0.12M | −€0.17M | €2.74M (6.3%) |

*Volume: FTE above plan at budget cost per FTE. Mix: departments with higher cost per FTE grew more. Rate: actual against budget cost per FTE, at actual FTE.*

The five largest overruns by department:

| Employer | Department | Budget FTE | Actual FTE | Variance | of which volume |
|---|---|---:|---:|---:|---:|
| IT · Milan | Operations | 226 | 245 | €1,019k | €1,127k |
| PL · Kraków | Tech | 164 | 180 | €735k | €873k |
| PL · Kraków | Operations | 262 | 283 | €631k | €824k |
| IT · Milan | Sales | 112 | 119 | €626k | €390k |
| IT · Milan | Finance | 90 | 101 | €578k | €748k |

All 12 departments ran above planned FTE. The largest overruns were in Operations (IT · Milan), Tech (PL · Kraków) and Operations (PL · Kraków), where extra headcount met a high cost per FTE.

## 2. What a fully loaded employee costs

| Employer | Cost per FTE, June 2026 | Employer social contributions | TFR | Contribution rules |
|---|---:|---:|---:|---|
| IT · Milan | €59,382 | 29.8% of gross pay | 7.0% of gross pay | INPS pension 23.81%, other INPS and INAIL 6.0% (illustrative), TFR at base pay / 13.5 |
| PL · Kraków | €41,727 | 20.7% of gross pay | - | ZUS pension 9.76% and disability 6.50% up to the annual cap; accident 1.67%, Labour Fund 2.45%, FGŚP 0.10%, PPK 1.5% on 50% of pay |

*Gross pay is base pay at contracted FTE plus target bonus. In Poland, 79 of 1,362 employees earn above the 2026 cap of 282,600 PLN (€66,388 at 4.2568 PLN per euro), so their pension and disability contributions stop part-way through the year.*

## 3. FY2027 under four scenarios

![Scenario costs](figures/03_scenario_costs.svg)

| Scenario | People cost | Change vs FY2026 | Average FTE | Closing FTE | Hires | Hiring cost | Remediation |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | €111.0M | +3.6% | 2,172 | 2,172 | 382 | €1.22M | - |
| Hiring freeze | €104.6M | −2.3% | 2,049 | 1,895 | 86 | €0.27M | - |
| High attrition | €110.7M | +3.3% | 2,166 | 2,161 | 484 | €1.54M | - |
| Pay equity first | €111.7M | +4.3% | 2,172 | 2,172 | 382 | €1.22M | €0.76M |

*People cost = payroll plus pay-equity remediation; hiring cost is shown apart. Scenario settings: Base - attrition x1.0, replacement 90%, growth x1.0; Hiring freeze - attrition x1.0, replacement 90%, growth x0.0, freeze from month 4; High attrition - attrition x1.3, replacement 90%, growth x1.0; Pay equity first - attrition x1.0, replacement 90%, growth x1.0, remediation from month 7.*

![FTE paths](figures/04_fte_paths.svg)

FY2026 attrition was 16.9% in Italy and 18.2% in Poland. The forecast backfills 90% of leavers after 2 months, so each extra point of attrition adds about €62k of recruitment cost at the assumed cost per hire.

## 4. Recommendations

1. **Set the FY2027 budget at the base case plus pay-equity remediation, €111.7M.** The first pay-transparency reports cover 2026 pay and are due in June 2027; gaps that are neither justified nor closed within six months lead to a joint pay assessment.
2. **Control headcount by position, month by month.** The FY2026 overrun was volume, and actual FTE was already more than 2% above plan by August 2025.
3. **Treat a hiring freeze as an operating decision.** It saves money only by ending the year 278 FTE short.
4. **Price attrition in the budget.** Recruitment cost rises with every leaver, even when payroll does not.
5. **Replace the illustrative rates with the payroll provider's:** other INPS contributions and INAIL, the Polish accident rate, PPK participation, and cost per hire.

## 5. Method and limits

- **Two engines, one answer.** Every figure is computed in pandas and again by live formulas in [the workbook](../deliverables/workforce_cost_model.xlsx); its Reconciliation sheet checks each pair, and CI recalculates the workbook with LibreOffice.
- **Month-end population.** FTE and cost are counted on the payroll at each month end, from hire and exit dates.
- **Simplifications, stated.** Salaries as at 30 June 2026 apply to every month; bonus is paid at target; TFR accrues on base pay; one cap and one exchange rate apply to the whole year; overtime, leave and benefits in kind are not modelled. Full list in [docs/method.md](../docs/method.md).
- **Not payroll or tax advice.** Rates and caps carry their source and status in [docs/verification.md](../docs/verification.md).

