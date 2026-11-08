# Method

How every number in the model is produced. The same rules are written twice, in pandas
([`src/model.py`](../src/model.py)) and as live formulas in the workbook
([`src/build_workbook.py`](../src/build_workbook.py)), and the Reconciliation sheet checks that
the two agree. Rates and caps carry their source in [verification.md](verification.md).

## Population and calendar

| Choice | This model | Why |
|---|---|---|
| Employers | The Italian (Milan) and Polish (Kraków) entities of the organisation in hr-people-analytics | Two contribution systems with different logic: an Italian severance accrual, a Polish annual cap. |
| Fiscal year | July to June. FY2026 = 1 July 2025 to 30 June 2026; FY2027 = the year after | FY2026 ends on the snapshot date of the source data. |
| Who counts | Anyone on the payroll at some point in FY2026: hired on or before 30 June 2026 and still employed after 30 June 2025 | The roster must hold joiners and leavers, or the budget variance has nothing to explain. |
| On the payroll at a date | hire date ≤ date < exit date | A leaver is off the payroll from the exit date. The workbook uses the same test with `SUMIFS` and an exit date of 31 December 2099 for people still employed. |
| Month | The payroll at each month end | FTE and cost in a month are those of the people on the payroll at its last day. |

## Fully loaded cost per employee

| Step | Rule |
|---|---|
| Base pay | full-time salary × FTE |
| Bonus | base pay × target for the job level, paid at target |
| Gross pay | base pay + bonus |
| Italy: employer social contributions | gross pay × (INPS pension 23.81% + other INPS and INAIL 6.0%) |
| Italy: TFR | base pay ÷ 13.5 |
| Poland: employer social contributions | min(gross pay, cap) × (pension 9.76% + disability 6.50%) + gross pay × (accident 1.67% + Labour Fund 2.45% + FGŚP 0.10% + PPK 1.5% × participation 50%) |
| Poland: cap in euro | 282,600 PLN ÷ 4.2568 |
| Loaded cost | gross pay + employer social contributions + TFR |

A month costs one twelfth of the loaded annual cost of everyone on the payroll at its end.

## FY2026: budget, actual and variance

- **Budget.** Set on 30 June 2025: the FTE on the payroll that day, by entity and department,
  grows in a straight line to the department's planned growth by month 12. Budget cost per FTE is
  the loaded cost per FTE of that opening population.
- **Actual.** The month-end payroll, as above.
- **Variance by department**, on average FTE (Af, Bf) and cost per FTE over the year (Ar, Br):
  - volume = (Af − Bf) × Br
  - rate = (Ar − Br) × Af
  - volume + rate = Af × Ar − Bf × Br = actual cost − budget cost, exactly.
- **Variance by entity.** Entity volume = (entity Af − entity Bf) × entity Br. The mix effect is
  the sum of department volumes minus the entity volume: positive when departments with a
  higher budget cost per FTE ran further ahead of plan. Entity rate is the sum of department
  rates. Volume + mix + rate = the entity variance.

**Why the rate effect is not pay inflation.** The source has one salary per person, so the
model applies it to every month (see [simplifications](#simplifications)). A rate
variance here comes from who was on the payroll: joiners paid less than the people they joined
lower the cost per FTE.

## FY2027: the forecast

Every entity × department cell starts from the payroll at 30 June 2026 (starting FTE S and cost
per FTE R) and runs month by month:

| Quantity | Rule |
|---|---|
| Monthly attrition a | FY2026 leavers' FTE ÷ average month-end FTE in FY2026 ÷ 12 × the scenario's attrition multiplier |
| Leavers(m) | FTE(m − 1) × a |
| Backfills(m) | Leavers(m − T) × replacement ratio, where T is the time to hire (2 months). Before month T + 1, the replacement ratio applies to S × a, the leavers of a steady month. |
| Growth hires(m) | S × planned annual growth × the scenario's growth multiplier ÷ 12 |
| Hires(m) | Backfills + growth hires; zero from the hiring-freeze month |
| FTE(m) | FTE(m − 1) − leavers + hires |
| Cost(m) | FTE(m) × R × FX × (1 + pay review from January 2027) × (1 + collective renewal from its month) ÷ 12 |
| Hiring cost(m) | hires × cost per hire, reported apart from people cost |
| Remediation(m) | from its start month: annual remediation ÷ 12 × the entity's on-cost factor × FX |
| FX | 1, except in Poland: the June 2026 EUR/PLN rate ÷ the scenario's rate. Polish pay is set in zloty and every Polish rule (the ZUS cap included) is in PLN, so the euro cost scales exactly |
| Collective renewal | the entity's rise from its month, only in scenarios that switch renewals on: 1.5% in Italy from November 2026, 2.0% in Germany and 1.0% in Spain from January 2027, none in Poland (illustrative) |

The on-cost factor turns a euro of extra base pay into loaded cost, with no cap applied:
1 + 23.81% + 6.0% + 1 ÷ 13.5 in Italy; 1 + every Polish rate above in Poland. Remediation comes
from pay-transparency-readiness-kit, which prices closing each flagged category gap at the upper
bound; it is added from month 7 so that gaps are being closed before the first reports are due
in June 2027.

In the workbook, the backfill formula looks up the leavers of month m − T with `INDEX` over
the months to its left only. A range that included the current month would be a circular
reference.

### Scenarios

| Scenario | Attrition | Replacement | Growth | Hiring freeze | Remediation | Renewals | EUR/PLN |
|---|---:|---:|---:|---|---|---|---:|
| Base | × 1.0 | 90% | × 1.0 | none | none | off | 4.2568 |
| Hiring freeze | × 1.0 | 90% | × 0 | from October 2026 | none | off | 4.2568 |
| High attrition | × 1.3 | 90% | × 1.0 | none | none | off | 4.2568 |
| Pay equity first | × 1.0 | 90% | × 1.0 | none | from January 2027 | off | 4.2568 |
| Cost pressure | × 1.0 | 90% | × 1.0 | none | none | on | 4.00 |

The Settings sheet holds the same table: change a cell and the scenario sheets, the Scenarios
summary and the Dashboard follow. The Dashboard shows the scenario picked in Settings.

### Bridge from FY2026 to FY2027

For each scenario and entity, with FY2026 average FTE and cost per FTE (F₀, R₀) and the FY2027
equivalents (F₁, R₁) on payroll only:

- volume = (F₁ − F₀) × R₀
- rate = (R₁ − R₀) × F₁
- FY2026 cost + volume + rate + remediation = FY2027 people cost

The memo splits the base-case rate effect further: the pay review's own cost, computed from the
forecast, and the remainder, which is the lower cost per FTE of the June 2026 workforce.

## FY2027 after the closed months: the 4+8 outlook

The budget for FY2027 is the base case, approved in June 2026. By the October close, four months
have happened. Their actuals (month-end FTE, leavers, hires and payroll cost by cell) are
**synthetic**: [`src/ytd.py`](../src/ytd.py) writes them from the June 2026 population with drivers
that depart from the plan on purpose (Customer Service attrition × 1.5, Tech hiring 40% of its
planned growth, pay 1.2% above June in Kraków and 0.4% in Munich) and rounds them as a payroll
extract would. The workbook holds them as values on the Actuals FY27 sheet, and the number of
closed months is counted from there: add a month and the outlook rolls forward.

For each cell, with k closed months:

| Quantity | Rule |
|---|---|
| Months 1 to k | the actuals |
| Monthly attrition a | leavers ÷ FTE, summed over the closed months (the plan's rate when k = 0) |
| Cost per FTE | the last closed month's run-rate: cost(k) × 12 ÷ FTE(k); from the pay review's month × (1 + review), unless already in the run-rate |
| Months k + 1 to 12 | the base case's rules from FTE(k): leavers, backfills of the leavers T months earlier (closed months included), planned growth |

Outlook against budget, by entity, with average FTE and cost per FTE (Fb, Rb budget; Fo, Ro outlook):
volume = (Fo − Fb) × Rb, rate = (Ro − Rb) × Fo, and volume + rate = the variance. With no closed
months the outlook is the base case, which a test checks.

## The headcount plan

The business sets the FTE it wants at 30 June 2027, as a change on 30 June 2026 by department
(Customer Service −3%, Tech +10%, Sales +5%, the rest flat: illustrative). A search opened after the
October close fills a post T months later, so until month p = k + T the plan has the outlook's
hires, already in the pipeline. From month p + 1, the same h hires each month for n = 12 − p months.
With q = 1 − a and F the FTE at month p, FTE after n months is F × qⁿ + h × (1 − qⁿ) ÷ a, so

  h = max(0, (target − F × qⁿ) × a ÷ (1 − qⁿ)), or (target − F) ÷ n with no attrition.

When h is positive the plan lands on the target exactly; when it is zero, the cell would close at
or above its target even without hiring, and the plan says so rather than proposing exits. Cost follows the outlook's cost per FTE; hiring cost is h ×
cost per hire. The workbook writes h as one formula with `POWER`, and the Reconciliation sheet
checks it for every cell.

## Three engines, one answer

A third engine runs in the browser: the [scenario simulator](https://d0m3n1c0x.github.io/workforce-cost-model/simulator/)
recomputes `forecast()`, `summary()`, `outlook()`, `plan()` and `outlook_summary()` for any choice of levers, and
what one employee costs in four countries (`src/employer_cost.py`). `tests/js/check_engine.mjs` compares it with the
model on 43,152 values (thirteen scenarios, six outlooks and plans with different closed months, targets, time to hire
and pay review months, 68 pay levels around every ceiling, a client-like roster) in CI. For a client's own staff no
month has closed, so the outlook is the base case and the plan starts from July.

- The pandas model and the workbook are built from the same `config.py`. The workbook holds no
  pasted results except the Python column of the Reconciliation sheet.
- The Reconciliation sheet compares Python and formula values for every entity × department
  × month of the actuals, the budget, the variance, the drivers, each scenario, the Scenarios
  summary, the Dashboard, a sample of employees, each country's total cost, the closed months, the outlook, the
  headcount plan and the outlook against budget: 1649 checks. A value matches within
  1 part in 10⁹. The sheet also counts Polish salaries below the minimum wage (none).
- `openpyxl` writes formulas without results. CI recalculates the whole workbook with
  LibreOffice and [`check_workbook.py`](../src/check_workbook.py) fails on any mismatch and on
  any formula error anywhere. Locally, the test suite builds a sample workbook (two stayers,
  leavers and joiners per department) and calculates it with the pure-Python `formulas`
  package. A test changes one Python value by a millionth and checks the mismatch is caught.
- Excel details that matter: no dynamic arrays, `SUMIFS` with `"<="&date` criteria (dates are
  whole numbers, so the text conversion is exact), and full calculation on load.

## Simplifications

Stated here so a reviewer can judge them; each one is where a real budget would use payroll data.

- **One salary for the year.** The source has one salary per person, and the model applies it
  to every month of FY2026. There is no pay history.
- **Bonus at target**, accrued evenly. No performance multiplier, no timing of payment.
- **TFR on base pay only**, no revaluation of the fund and no transfer to pension funds.
- **The Polish cap is applied to annualised pay.** In payroll it applies to pay in a calendar
  year, and contributions stop in the month the cap is reached. The model spreads them evenly,
  ignores that the fiscal year straddles two calendar years, and caps joiners and leavers on
  their annualised pay rather than on what they earned in the year.
- **A client's staff in the simulator** start from today's run-rate (today's FTE at today's loaded cost, for a
  year), with one leavers rate and one growth rate for everyone: a snapshot carries no history.
- **Ceilings the model leaves out**, which overstate the cost of high earners a little: the German accident
  insurance is charged on all pay, while each Berufsgenossenschaft caps it at its own maximum annual earnings; the
  Italian IVS contribution has a ceiling for people first insured after 1995, and 0.50 points of it are offset
  against the TFR, neither of which the model applies.
- **One exchange rate a scenario** for the whole year. The Cost pressure scenario prices Polish pay at
  4.00 PLN per euro; a finance team would budget at its own planning rate.
- **Renewals as one rise on the whole payroll**, from one month. A real renewal raises minimums by
  grade, and personal supplements may absorb part of it.
- **The outlook keeps the plan's rules after the closed months**: only attrition and cost per FTE
  are re-based. A finance team would also revisit growth and the time to hire.
- **Not modelled:** overtime, holiday accruals, benefits in kind, severance on exit, reduced
  contributions for particular hires, and contractors.
- **FTE, not positions.** The forecast moves fractional FTE, as a driver-based plan does;
  position control would round them to people.
- **Synthetic company.** The budget, growth plans, pay review, renewals, replacement ratio, cost per
  hire, the closed months of FY2027 and the headcount plan are invented (see the register).
