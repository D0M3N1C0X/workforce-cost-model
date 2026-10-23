// The model's engine in the browser: a line-by-line twin of src/employer_cost.py and of forecast() and summary() in
// src/model.py. tests/js/check_engine.mjs runs it on the cases the model computed (tests/fixtures/js_vectors.json)
// and CI fails at the first difference. Nothing here touches the page or the network.

// ---- What one employee costs (employer_cost.items / total) ---------------------------------------------------
export function employerItems(country, gross, base, R) {
  base = base ?? gross;
  if (country === "IT") return { social: gross * R.IT_IVS + gross * R.IT_OTHER, tfr: base / R.TFR_DIVISOR };
  if (country === "PL") {
    const capped = Math.min(gross, R.PL_CAP_PLN / R.EUR_PLN);
    return { pension_disability: capped * R.PL_PENSION + capped * R.PL_DISABILITY, accident: gross * R.PL_ACCIDENT,
      funds: gross * R.PL_LABOUR_FUND + gross * R.PL_FGSP, ppk: gross * R.PL_PPK * R.PPK_PARTICIPATION };
  }
  if (country === "DE") {
    const rv = Math.min(gross, R.DE_CAP_PENSION), kv = Math.min(gross, R.DE_CAP_HEALTH);
    return { pension_unemployment: rv * R.DE_PENSION + rv * R.DE_UNEMPLOYMENT,
      health_care: kv * (R.DE_HEALTH + R.DE_HEALTH_EXTRA) + kv * R.DE_CARE,
      levies: rv * R.DE_INSOLVENCY + rv * R.DE_U2, accident: gross * R.DE_ACCIDENT };
  }
  if (country === "ES") {
    const b = Math.min(gross, R.ES_CAP), bands = R.ES_SOLIDARITY;
    let solidarity = 0;
    bands.forEach(([floor, rate], k) => {
      const top = k + 1 < bands.length ? bands[k + 1][0] : Infinity;
      solidarity += Math.max(0, Math.min(gross, top) - floor) * rate;
    });
    return { common_mei: b * R.ES_COMMON + b * R.ES_MEI,
      unemployment_funds: b * R.ES_UNEMPLOYMENT + b * R.ES_FOGASA + b * R.ES_TRAINING,
      accident: b * R.ES_ACCIDENT, solidarity };
  }
  throw new Error(`no employer-cost rules for ${country}`);
}

export function employerTotal(country, gross, base, R) {
  let out = gross;
  for (const v of Object.values(employerItems(country, gross, base, R))) out += v;
  return out;
}

// ---- A client's roster: cells of country and department, with FTE and loaded cost per FTE ---------------------
// rows: { country, department, fte, base (annual salary at full time), bonus (annual) }
export function cellsFromRoster(rows, R) {
  const cells = new Map();
  for (const r of rows) {
    const gross = r.base * r.fte + r.bonus;
    const loaded = employerTotal(r.country, gross, r.base * r.fte, R);
    const k = `${r.country}\u0000${r.department}`;
    if (!cells.has(k)) cells.set(k, { country: r.country, department: r.department, fte: 0, cost: 0 });
    const c = cells.get(k);
    c.fte += r.fte; c.cost += loaded;
  }
  return [...cells.values()].map((c) => ({ ...c, rate: c.cost / c.fte }));
}

// ---- FY2027 month by month (model.forecast) -----------------------------------------------------------------------
// cells: { country, department, fte, rate, attrition (a year), growth (a year) }
// scenario: { attrition_x, replacement, growth_x, freeze_from, remediation_from }
// p: { months, merit: {country}, merit_month, time_to_hire, cost_per_hire: {country}, remediation: {country},
//      loaded_factor: {country} }
export function forecast(cells, scenario, p) {
  const months = [];
  for (const s of cells) {
    const a = (s.attrition * scenario.attrition_x) / 12;
    const g = s.growth * scenario.growth_x;
    let prev = s.fte;
    const hist = [];
    for (let m = 1; m <= p.months; m++) {
      const leavers = prev * a;
      const backfill = m > p.time_to_hire ? hist[m - 1 - p.time_to_hire] : s.fte * a;
      const frozen = scenario.freeze_from > 0 && m >= scenario.freeze_from;
      const hires = frozen ? 0 : backfill * scenario.replacement + (s.fte * g) / 12;
      const fte = prev - leavers + hires;
      const rate = s.rate * (1 + (p.merit[s.country] ?? 0) * (m >= p.merit_month ? 1 : 0));
      months.push({ country: s.country, department: s.department, month: m, leavers, hires, fte,
        cost: (fte * rate) / 12, hiring_cost: hires * (p.cost_per_hire[s.country] ?? 0) });
      hist.push(leavers);
      prev = fte;
    }
  }
  const countries = [...new Set(cells.map((c) => c.country))];
  const remediation = [];
  for (const c of countries) {
    for (let m = 1; m <= p.months; m++) {
      remediation.push({ country: c, month: m, remediation: scenario.remediation_from > 0 && m >= scenario.remediation_from
        ? ((p.remediation[c] ?? 0) * p.loaded_factor[c]) / 12 : 0 });
    }
  }
  return { months, remediation };
}

// ---- The year by entity, with the bridge from the baseline (model.summary) ---------------------------------------
// baseline: { country: { fte (average), cost (a year) } }
const sum = (xs) => xs.reduce((s, x) => s + x, 0);
export function summary({ months, remediation }, baseline, p) {
  const countries = [...new Set(months.map((r) => r.country))];
  return countries.map((c) => {
    const fy = months.filter((r) => r.country === c);
    const byMonth = [];
    for (let m = 1; m <= p.months; m++) byMonth.push(sum(fy.filter((r) => r.month === m).map((r) => r.fte)));
    const a_fte = baseline[c].fte, a_cost = baseline[c].cost;
    const f_fte = sum(byMonth) / p.months, f_cost = sum(fy.map((r) => r.cost));
    const rem = sum(remediation.filter((r) => r.country === c).map((r) => r.remediation));
    const a_rate = a_cost / a_fte, f_rate = f_cost / f_fte;
    return { country: c, fy26_fte: a_fte, fy26_cost: a_cost, fy27_fte: f_fte, closing_fte: byMonth[p.months - 1],
      fy27_payroll: f_cost, fy27_remediation: rem, fy27_cost: f_cost + rem, fy27_hires: sum(fy.map((r) => r.hires)),
      fy27_hiring_cost: sum(fy.map((r) => r.hiring_cost)), bridge_volume: (f_fte - a_fte) * a_rate,
      bridge_rate: (f_rate - a_rate) * f_fte, bridge_remediation: rem };
  });
}

// The month totals a chart needs: FTE at month end and cost in the month, across every entity.
export function monthly({ months, remediation }, p) {
  const out = [];
  for (let m = 1; m <= p.months; m++) {
    const rows = months.filter((r) => r.month === m);
    out.push({ month: m, fte: sum(rows.map((r) => r.fte)),
      cost: sum(rows.map((r) => r.cost)) + sum(remediation.filter((r) => r.month === m).map((r) => r.remediation)) });
  }
  return out;
}

export function number(v, decimalComma) {
  if (typeof v === "number") return v;
  let t = String(v ?? "").replace(/[\s€$£]|zł|PLN|EUR/gi, "");
  if (t === "") return 0;
  if (decimalComma) t = t.replace(/\./g, "").replace(",", ".");
  else if (/^-?\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)) t = t.replace(/,/g, "");
  const n = Number(t);
  if (Number.isNaN(n)) throw new Error(`not a number: "${v}"`);
  return n;
}
