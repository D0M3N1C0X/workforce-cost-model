// Recomputes with web/engine.js every case the model computed, and exits with 1 at the first difference.
import { readFileSync } from "node:fs";
import { employerItems, employerTotal, cellsFromRoster, forecast, summary, outlook, plan, outlookSummary }
  from "../../web/engine.js";

const V = JSON.parse(readFileSync(new URL("../fixtures/js_vectors.json", import.meta.url)));
const close = (a, b) => (typeof b === "number" ? Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b)) : a === b);
let checks = 0, failures = 0;
const expect = (ok, what) => { checks++; if (!ok) { failures++; if (failures <= 20) console.error("difference:", what); } };
const R = V.cfg.rules;

for (const c of V.cases) {
  const p = { months: V.cfg.months, merit: c.merit, merit_month: V.cfg.merit_month, time_to_hire: c.time_to_hire,
    cost_per_hire: V.cfg.cost_per_hire, remediation: V.sample.remediation, loaded_factor: V.cfg.loaded_factor,
    eur_pln: V.cfg.eur_pln, renewal: c.renewal ?? V.cfg.renewal };
  const f = forecast(V.sample.cells, c.scenario, p);
  expect(f.months.length === c.months.length, `${c.scenario.name}: ${f.months.length} rows vs ${c.months.length}`);
  c.months.forEach(([country, dept, m, fte, hires, cost, hiring], i) => {
    const a = f.months[i] || {};
    expect(a.country === country && a.department === dept && a.month === m, `${c.scenario.name} row ${i} key`);
    for (const [k, v] of [["fte", fte], ["hires", hires], ["cost", cost], ["hiring_cost", hiring]])
      expect(close(a[k], v), `${c.scenario.name} ${country} ${dept} m${m} ${k}: ${a[k]} vs ${v}`);
  });
  c.remediation.forEach(([country, m, v], i) => expect(f.remediation[i].country === country && close(f.remediation[i].remediation, v),
    `${c.scenario.name} remediation ${country} m${m}`));
  const s = summary(f, V.sample.baseline, p);
  for (const e of c.summary) {
    const a = s.find((r) => r.country === e.country) || {};
    for (const [k, v] of Object.entries(e)) expect(close(a[k], v), `${c.scenario.name} ${e.country} ${k}: ${a[k]} vs ${v}`);
  }
}
const base = V.cfg.scenarios[0];
V.outlooks.forEach((c, n) => {
  const p = { months: V.cfg.months, merit: c.merit, merit_month: c.merit_month, time_to_hire: c.time_to_hire,
    cost_per_hire: V.cfg.cost_per_hire };
  const ol = outlook(V.sample.cells, c.closed, base, p);
  const pl = plan(ol, c.plan_target, p);
  const rows = (got, want, what) => {
    expect(got.length === want.length, `${what} ${n}: ${got.length} rows vs ${want.length}`);
    want.forEach(([country, dept, m, ...vals], i) => {
      const a = got[i] || {};
      expect(a.country === country && a.department === dept && a.month === m, `${what} ${n} row ${i} key`);
      ["fte", "leavers", "hires", "cost", "hiring_cost"].forEach((k, j) =>
        expect(close(a[k], vals[j]), `${what} ${n} ${country} ${dept} m${m} ${k}: ${a[k]} vs ${vals[j]}`));
    });
  };
  rows(ol.months, c.outlook, "outlook");
  rows(pl.months, c.plan, "plan");
  for (const [got, want, what] of [[ol.cells, c.outlook_cells, "outlook cell"], [pl.cells, c.plan_cells, "plan cell"]])
    want.forEach((e, i) => { for (const [k, v] of Object.entries(e)) expect(close(got[i]?.[k], v), `${what} ${n} ${i} ${k}: ${got[i]?.[k]} vs ${v}`); });
  const s = outlookSummary(c.budget, ol, pl, p);
  for (const e of c.summary) {
    const a = s.find((r) => r.country === e.country) || {};
    for (const [k, v] of Object.entries(e)) expect(close(a[k], v), `outlook summary ${n} ${e.country} ${k}: ${a[k]} vs ${v}`);
  }
});
for (const [c, g, items, total] of V.costs) {
  const a = employerItems(c, g, g * 0.9, R);
  for (const [k, v] of Object.entries(items)) expect(close(a[k], v), `${c} ${g} ${k}: ${a[k]} vs ${v}`);
  expect(close(employerTotal(c, g, g * 0.9, R), total), `${c} ${g} total`);
}
const cells = cellsFromRoster(V.roster, R);
expect(cells.length === V.cells.length, `roster: ${cells.length} cells vs ${V.cells.length}`);
V.cells.forEach((e, i) => { for (const k of ["country", "department", "fte", "cost", "rate"]) expect(close(cells[i]?.[k], e[k]), `roster cell ${i} ${k}: ${cells[i]?.[k]} vs ${e[k]}`); });
console.log(`${checks - failures} of ${checks} values agree with the model in ${V.cases.length} scenarios, ${V.outlooks.length} outlooks and plans, ${V.costs.length} pay levels and a roster`);
process.exit(failures ? 1 : 0);
