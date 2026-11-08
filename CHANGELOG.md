# Changelog

What changed in each release. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2.0.0] - 2026-11-06

### Added

- **Munich and Barcelona join the model.** The organisation's German and Spanish entities, already in the source data,
  are now priced and forecast like Milan and Kraków: German pension, unemployment, health and care insurance with
  their two ceilings, levies and accident insurance; Spanish Seguridad Social up to the maximum base and the
  solidarity contribution above it. FY2026 is now €185.5M for 3,311 FTE, FY2027 €192.9M in the base case.
- Settings sheet sections for Germany and Spain; one Roster formula per country, with the ceilings and the Spanish
  solidarity bands; totals by country and counts of employees above each ceiling on the Reconciliation sheet
  (1086 checks, was 570).
- German and Spanish pay-gap costs from pay-transparency-readiness-kit (W15), pay review 3% and cost per hire.

### Changed

- The Dashboard, the CFO memo and the charts cover all four entities. The simulator is checked on 18,919 values
  (was 9,679).

## [1.2.1] - 2026-10-23

### Fixed

- Simulator: semicolon CSV files with dot decimals are read correctly (design base 1.1.0) and "80%" works as a
  full-time share; growth cannot go below zero, which produced negative hires; a scenario with the same levers as
  the one on screen is no longer shown twice, and a different one with a name already used gets a number; moving a
  lever no longer rounds the pay-gap amounts; countries missing from a saved scenario take the default pay review;
  a file with no FTE says so; the view is kept in the address; "one hire" in the singular.
- README: the hiring freeze ends with 278 fewer FTE than the base case (the simulator compares with today: 277).
- method.md names the three engines and the ceilings the model leaves out.

## [1.2.0] - 2026-10-23

### Added

- **[Scenario simulator](https://d0m3n1c0x.github.io/workforce-cost-model/simulator/)** in the browser: levers for
  leavers, backfills, growth, a hiring freeze, the pay review and closing pay gaps; FY2027 month by month, the
  bridge and the sentence for the CFO; scenarios saved and compared side by side; an Excel download and a print
  view. It runs on the sample company or on a client's own staff list (Excel or CSV), which never leaves the
  computer. English and Italian.
- **What one employee costs** in Italy, Poland, Germany and Spain, item by item (`src/employer_cost.py`). German and
  Spanish 2026 rates and ceilings, with their sources, are entries W22-W32 of the
  [verification register](docs/verification.md).
- `web/engine.js` is a twin of `forecast()`, `summary()` and `employer_cost`, checked against the model on 9,679
  values in CI (`tests/js/check_engine.mjs`).

## [1.1.0] - 2026-10-09

### Changed

- Reconciliation, recalculation and byte-stable files through [excel-twin](https://github.com/D0M3N1C0X/excel-twin).

## [1.0.0] - 2026-09-30

First complete release: the Excel model, the CFO memo and the pipeline that reconciles them.

[Unreleased]: https://github.com/D0M3N1C0X/workforce-cost-model/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/D0M3N1C0X/workforce-cost-model/releases/tag/v1.2.1
[1.2.0]: https://github.com/D0M3N1C0X/workforce-cost-model/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/workforce-cost-model/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/workforce-cost-model/releases/tag/v1.0.0
