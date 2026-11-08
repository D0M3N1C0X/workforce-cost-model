# FY2027 people cost: Italy, Poland, Germany and Spain

**Scope:** IT · Milan, PL · Kraków, DE · Munich and ES · Barcelona, 3,311 FTE on average in FY2026
**Model:** fully loaded cost per employee, FY2026 budget against actual, FY2027 month by month under five scenarios, the outlook after October and a headcount plan, in a live Excel model reconciled with pandas
**Data:** synthetic, the organisation analysed in [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics); rates and caps for 2026 from the sources in [docs/verification.md](../docs/verification.md)

> Fiscal years run July to June. The budget, growth plans, pay review, renewals, cost per hire, the July-October 2026 actuals and the headcount plan are invented for the demonstration; the employer-cost rules are real and dated.

## The answer

- **FY2026 closed €9.9M (5.6%) over budget, at €185.5M.** Headcount ran ahead of plan: volume added €10.3M, the department mix €0.09M, while cheaper joiners saved €0.50M.
- **FY2027 costs €192.9M in the base case (+4.0%).** More FTE add €4.6M: the year opens with the headcount FY2026 closed on, and Customer Service, Tech and Sales keep growing. Cost per FTE adds €2.8M, where the January pay review (2.5% in Italy, 5.0% in Poland, 3.0% in Germany and 3.0% in Spain) adds €3.2M and the lower cost per FTE of the June 2026 workforce takes back €0.3M.
- **A hiring freeze from October would cut FY2027 to €182.6M** (−1.6%), but the year would close with 411 fewer FTE than the base case: a capacity decision, not a finance one.
- **Higher attrition barely moves payroll but costs in hiring.** With attrition 30% higher (5.0 points), vacancies offset the backfills, while recruitment rises to €2.49M (€0.52M more).
- **Starting to close pay gaps in January 2027, before the first pay-transparency reports are due, adds €1.23M to FY2027** and €2.46M in every full year after, loaded with employer costs. The gaps come from [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit).
- **Collective renewals and a stronger zloty would add €4.45M**, to €197.3M: renewals of 1.5% in Italy from November, 2.0% in Germany from January and 1.0% in Spain from January, and 4.00 zloty to the euro instead of 4.2568, which alone adds €3.12M to Polish pay set in zloty.
- **After October, FY2027 is heading for €193.1M, €0.18M over budget, for the wrong reasons.** 10 fewer FTE than planned on average save €0.60M; a higher cost per FTE adds €0.77M, 74% of it in Kraków. More leavers also lift recruitment to €2.28M (€0.31M over budget).
- **Landing on the June 2027 headcount plan, 3,433 FTE, takes 64 hires a month from January** and adds €1.15M to the outlook's payroll: searches for those posts have to open now.

## 1. FY2026: where the budget went

![Budget and actual FTE](figures/01_fte_budget_actual.svg)

![Variance bridge](figures/02_variance_bridge.svg)

| Employer | Budget | Actual | Volume | Mix | Rate | Variance |
|---|---:|---:|---:|---:|---:|---:|
| IT · Milan | €57.7M | €60.8M | €3.51M | €0.06M | −€0.51M | €3.06M (5.3%) |
| PL · Kraków | €43.6M | €46.3M | €2.79M | €0.12M | −€0.17M | €2.74M (6.3%) |
| DE · Munich | €49.6M | €52.6M | €2.84M | −€0.06M | €0.17M | €2.94M (5.9%) |
| ES · Barcelona | €24.6M | €25.8M | €1.19M | −€0.03M | €0.01M | €1.17M (4.8%) |

*Volume: FTE above plan at budget cost per FTE. Mix: departments with higher cost per FTE grew more. Rate: actual against budget cost per FTE, at actual FTE.*

The five largest overruns by department:

| Employer | Department | Budget FTE | Actual FTE | Variance | of which volume |
|---|---|---:|---:|---:|---:|
| IT · Milan | Operations | 226 | 245 | €1,019k | €1,127k |
| DE · Munich | Operations | 159 | 173 | €955k | €1,004k |
| PL · Kraków | Tech | 164 | 180 | €735k | €873k |
| PL · Kraków | Operations | 262 | 283 | €631k | €824k |
| IT · Milan | Sales | 112 | 119 | €626k | €390k |

All 24 departments ran above planned FTE. The largest overruns were in Operations (IT · Milan), Operations (DE · Munich) and Tech (PL · Kraków), where extra headcount met a high cost per FTE.

## 2. What a fully loaded employee costs

| Employer | Cost per FTE, June 2026 | Employer social contributions | TFR | Contribution rules |
|---|---:|---:|---:|---|
| IT · Milan | €59,382 | 29.8% of gross pay | 7.0% of gross pay | INPS pension 23.81%, other INPS and INAIL 6.0% (illustrative), TFR at base pay / 13.5 |
| PL · Kraków | €41,727 | 20.7% of gross pay | - | ZUS pension 9.76% and disability 6.50% up to the annual cap; accident 1.67%, Labour Fund 2.45%, FGŚP 0.10%, PPK 1.5% on 50% of pay |
| DE · Munich | €74,887 | 20.8% of gross pay | - | pension and unemployment 10.6% up to €101,400; health, additional contribution and care 10.55% up to €69,750; levies 0.59%, accident 1.08% (illustrative) |
| ES · Barcelona | €53,371 | 29.8% of gross pay | - | common contingencies and MEI 24.35%, unemployment, FOGASA and training 6.3%, AT/EP 1.5%, up to €61,214; solidarity contribution above it |

*Gross pay is base pay at contracted FTE plus target bonus. In Poland, 79 of 1,362 employees earn above the 2026 cap of 282,600 PLN (€66,388 at 4.2568 PLN per euro), so their pension and disability contributions stop part-way through the year. Ceilings bite harder elsewhere: 226 of 842 German employees earn above the health and care ceiling, and 64 of 569 Spanish ones above the maximum base, where the solidarity contribution takes over at a much lower rate.*

## 3. FY2027 under five scenarios

![Scenario costs](figures/03_scenario_costs.svg)

| Scenario | People cost | Change vs FY2026 | Average FTE | Closing FTE | Hires | Hiring cost | Remediation |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | €192.9M | +4.0% | 3,389 | 3,391 | 563 | €1.97M | - |
| Hiring freeze | €182.6M | −1.6% | 3,207 | 2,980 | 126 | €0.44M | - |
| High attrition | €192.4M | +3.7% | 3,380 | 3,375 | 713 | €2.49M | - |
| Pay equity first | €194.1M | +4.7% | 3,389 | 3,391 | 563 | €1.97M | €1.23M |
| Cost pressure | €197.3M | +6.4% | 3,389 | 3,391 | 563 | €1.97M | - |

*People cost = payroll plus pay-equity remediation; hiring cost is shown apart. Scenario settings: Base - attrition x1.0, replacement 90%, growth x1.0; Hiring freeze - attrition x1.0, replacement 90%, growth x0.0, freeze from month 4; High attrition - attrition x1.3, replacement 90%, growth x1.0; Pay equity first - attrition x1.0, replacement 90%, growth x1.0, remediation from month 7; Cost pressure - attrition x1.0, replacement 90%, growth x1.0, collective renewals, 4.00 PLN per euro.*

![FTE paths](figures/04_fte_paths.svg)

FY2026 attrition was 16.9% in Italy, 18.2% in Poland, 14.1% in Germany and 15.6% in Spain. The forecast backfills 90% of leavers after 2 months, so each extra point of attrition adds about €105k of recruitment cost at the assumed cost per hire.

## 4. FY2027 after October: outlook against budget

![Outlook against budget](figures/05_outlook_bridge.svg)

| Employer | Budget | July-October: actual against budget | Outlook | Variance | Volume | Rate | Hiring cost, outlook (against budget) |
|---|---:|---:|---:|---:|---:|---:|---:|
| IT · Milan | €62.3M | −€0.04M | €62.1M | −€0.19M (−0.3%) | −€0.19M | −€0.01M | €0.81M (+€0.11M) |
| PL · Kraków | €48.7M | +€0.16M | €49.1M | +€0.42M (+0.9%) | −€0.15M | +€0.57M | €0.59M (+€0.08M) |
| DE · Munich | €55.5M | +€0.04M | €55.5M | +€0.04M (+0.1%) | −€0.17M | +€0.21M | €0.62M (+€0.10M) |
| ES · Barcelona | €26.4M | −€0.02M | €26.4M | −€0.09M (−0.3%) | −€0.09M | €0.00M | €0.25M (+€0.02M) |

*Budget: the base case approved in June 2026. Outlook: actuals to October, then the base case's rules from where the year has got to, with the closed months' attrition and the last month's cost per FTE (4+8). The 4 closed months are synthetic: Customer Service losing 50% more people than in FY2026, Tech hiring 40% of its planned growth, pay in Kraków drifting 1.2% above June. The variance splits like FY2026's: volume at budget cost per FTE, rate at outlook FTE.*

## 5. The headcount plan

| Employer | Target, June 2027 | Outlook, June 2027 | Plan hires a month | Hires in FY2027 | Hiring cost | Payroll against outlook |
|---|---:|---:|---:|---:|---:|---:|
| IT · Milan | 1,049 | 1,031 | 20.0 | 221 | €0.88M | +€0.38M |
| PL · Kraków | 1,153 | 1,131 | 23.6 | 260 | €0.65M | +€0.34M |
| DE · Munich | 737 | 727 | 12.1 | 134 | €0.67M | +€0.28M |
| ES · Barcelona | 494 | 486 | 8.4 | 92 | €0.28M | +€0.15M |

*Targets against June 2026: Customer Service −3%, Tech +10% and Sales +5%, the rest flat (illustrative). Searches opened after the October close fill posts 2 months later; until then the outlook's backfills arrive. From then, the same hires each month: (target - FTE × q^n) × a / (1 - q^n), with a the monthly attrition, q = 1 - a and n the months left. The largest asks: Customer Service in Poland, 8.3 a month, Customer Service in Italy, 6.7 a month and Customer Service in Germany, 5.5 a month.*

## 6. Recommendations

1. **Set the FY2027 budget at the base case plus pay-equity remediation, €194.1M.** The first pay-transparency reports cover 2026 pay and are due in June 2027; gaps that are neither justified nor closed within six months lead to a joint pay assessment.
2. **Control headcount by position, month by month.** The FY2026 overrun was volume, and actual FTE was already more than 2% above plan by August 2025.
3. **Treat a hiring freeze as an operating decision.** It saves money only by ending the year 411 FTE short.
4. **Price attrition in the budget.** Recruitment cost rises with every leaver, even when payroll does not.
5. **Replace the illustrative rates with the payroll provider's:** other INPS contributions and INAIL, the Polish accident rate, PPK participation, the German insurer's additional contribution and accident rate, the Spanish AT/EP tariff, and cost per hire.
6. **Re-forecast every month from the run-rate.** After October the year is close to budget only because vacancies hide a rising cost per FTE; Kraków's pay drift needs an answer before the January review.
7. **Open the plan's searches now.** A post opened after the October close is filled in January at the earliest.

## 7. Method and limits

- **Two engines, one answer.** Every figure is computed in pandas and again by live formulas in [the workbook](../deliverables/workforce_cost_model.xlsx); its Reconciliation sheet checks each pair, and CI recalculates the workbook with LibreOffice.
- **Month-end population.** FTE and cost are counted on the payroll at each month end, from hire and exit dates.
- **Simplifications, stated.** Salaries as at 30 June 2026 apply to every month; bonus is paid at target; TFR accrues on base pay; one cap and one exchange rate apply to the whole year; overtime, leave and benefits in kind are not modelled. Full list in [docs/method.md](../docs/method.md).
- **Closed months are synthetic.** The July-October actuals are written by `src/ytd.py` from the June 2026 population with drivers that depart from the plan on purpose; they show the method, not a fact.
- **Not payroll or tax advice.** Rates and caps carry their source and status in [docs/verification.md](../docs/verification.md).

