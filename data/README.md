# Data

All synthetic. No real person's pay is in this repository.

| File | Made by | What it is |
|---|---|---|
| `source/employees.csv` | copied from [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics) at commit `201495b` | The 4,000-employee organisation analysed there, seed 42: the same file, with the same checksum, as in [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit). SHA-256 `3727232…7da79c`, pinned in `src/config.py` and checked on every build. |

The model reads eight columns and keeps the Italian and Polish entities:

| Column | Used as |
|---|---|
| `employee_id` | the row key on the Roster sheet |
| `country` | `IT` (Milan) or `PL` (Kraków); the German and Spanish entities are left out |
| `department`, `job_level` | the planning cell, and the bonus target |
| `fte` | 1.0 or 0.8 |
| `base_salary_eur` | full-time annual base salary, EUR |
| `hire_date`, `exit_date` | who is on the payroll at each month end; `exit_date` is empty for people still employed |

Everything else the model needs, from contribution rates to the FY2026 budget, is in
[`src/config.py`](../src/config.py), with its source or its status in
[docs/verification.md](../docs/verification.md).
