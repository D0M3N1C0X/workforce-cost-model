// The simulator's page: levers in, FY2027 out, scenarios saved and compared, one employee's cost in four countries.
// The calculations are in engine.js, verified against the Python model on every change; this file only moves data
// between the user and them. Nothing here talks to a server: inputs.json comes from this same page.
import { employerItems, employerTotal, cellsFromRoster, forecast, summary, monthly, number } from "./engine.js";
import { createI18n } from "./design/i18n.js";
import { readTable, matchColumns, applyMapping, savedMapping, rememberMapping, download, normalise } from "./design/table.js";
import { writeXlsx } from "./design/xlsx.js";

const { cfg: CFG, sample: SAMPLE } = await fetch("./inputs.json").then((r) => r.json());
const R = CFG.rules;

const UI = {
  en: {
    brand: "Workforce Cost Model", eyebrow: "People budget · FY2027", title: "What will next year's people cost be?",
    lead: "Move the levers - leavers, backfills, growth, a hiring freeze, the pay review, closing pay gaps - and see FY2027 cost, month by month, with the sentence for the CFO. On the sample company or on your own staff.",
    privacy: "Your staff file stays on this computer: the calculations run in this page and nothing is sent anywhere. You can check by going offline once the page has loaded.",
    vistaLabel: "View", vScenari: "Scenarios for FY2027", vCosto: "What one employee costs",
    step1: "Whose staff", datiEsempio: "The sample company: {n} FTE in Milan and Kraków at 30 June 2026, with the leavers and growth plan of the model. Load your own staff list to run the same scenarios on it.",
    datiCliente: "{f}: {n} employees, {fte} FTE in {p}. Leavers and growth below are yours to set.",
    dropOrganico: "Your staff list", dropOrganicoSub: "Optional · one row per employee: country, department, FTE, annual salary, bonus",
    tornaEsempio: "Use the sample company", modello: "Template:", modelloLink: "staff list", modifica: "Change",
    colonneOk: "All {n} columns needed were found", colonneSub: "Check the matches below, or change them.",
    colonneMancano: "Choose the column for {n} item(s) marked in red.", nonPresente: "— not in the file —", facoltativa: "optional",
    f_country: "Country (IT, PL, DE or ES)", f_department: "Department or cost centre", f_fte: "Full-time share (FTE)",
    f_base_salary: "Annual base salary, full time", f_bonus: "Annual bonus",
    cUscite: "Leavers a year, today", cUsciteSub: "Share of FTE who leave in a normal year.",
    cCrescita: "Planned growth a year", cCrescitaSub: "New FTE on top of backfills, as a share of today's FTE.",
    step2: "The scenario", nome: "Name", lUscite: "Leavers", lUsciteSub: "× today's rate: 1.3 means 30% more people leave.",
    lSostituzioni: "Leavers replaced", lSostituzioniSub: "Share of leavers backfilled, after the time to hire.",
    lCrescita: "Growth", lCrescitaSub: "× the growth plan: 0 means no new roles.",
    lBlocco: "Hiring freeze from", lBloccoSub: "No hires at all, not even backfills, from this month.",
    lTth: "Time to hire", lTthSub: "Months between a leaver and the backfill starting.", mesiN: "{n} months", mese1: "1 month",
    lMeseMerito: "Pay review from", lEquita: "Close pay gaps from",
    lEquitaSub: "Annual pay to add per country, before employer on-costs: the cost ceiling from the pay transparency tool.",
    nessuno: "Never", salva: "Save this scenario to compare", salvato: "Saved", nomeNuovo: "My scenario",
    stampaTitolo: "FY2027 people cost", perCfo: "For the CFO", mesi: "Month by month", mCosto: "Cost", mFte: "FTE",
    confronto: "Scenarios side by side", confrontoSub: "The scenario on screen and the ones you saved. Saved scenarios stay on this computer.",
    confrontoVuoto: "Save a scenario to compare it with others.",
    scaricaXlsx: "Download in Excel", stampa: "Print for the budget meeting", elimina: "Remove",
    kCosto: "FY2027 cost", kDelta: "Against {b}", kFte: "Average FTE", kChiusura: "FTE at 30 June 2027", kAssunzioni: "Hires and their cost",
    base26: "FY2026", baseOggi: "today's run-rate",
    hPaese: "Entity", hBase: "Starting point", hVolume: "Headcount", hTariffa: "Pay rates", hEquita: "Pay gaps", hFy27: "FY2027", hTotale: "Total",
    hScenario: "Scenario", hCosto: "FY2027 cost", hDelta: "Change", hFteMedi: "Average FTE", hFteFine: "Closing FTE", hAssunzioni: "Hires",
    hCostoAss: "Hiring cost", hEquitaC: "Pay gaps",
    frase: "{s}: FY2027 costs {c}, {d} {pm} than {b} ({cb}). Headcount {vv} {v}, pay rates {rv} {r}{e}. The year closes with {f} FTE, {df} {mf} than today{h}.",
    fraseEquita: ", closing pay gaps adds {x}", fraseAss: "; {n} hires cost {x} to recruit",
    piu: "more", meno: "less", piuFte: "more", menoFte: "fewer", aggiunge: "adds", toglie: "saves", aggiungono: "add", tolgono: "save",
    costoTitolo: "What one employee costs the employer", costoSub: "The same pay in four countries: gross pay plus every employer contribution, for a year of 2026.",
    kcRal: "Annual base salary, full time", kcBonus: "Annual bonus", kcFte: "Full-time share",
    rLordo: "Gross pay", rContributi: "Employer contributions", rTotale: "Total cost to the employer", rPct: "On top of gross pay",
    lordo: "Gross pay", oneri: "Employer contributions",
    costoNota: "Annual pay against annual ceilings, an approximation that is exact when pay is spread evenly over the year. Italy: other INPS contributions and INAIL at 6%, illustrative. Poland: PPK for half of pay, converted at the ECB rate. Germany: average additional health contribution and accident insurance at the 2025 trade-association average. Spain: open-ended contract, accident tariff for office work. Every rate and its source is in the verification register.",
    voci: { social: "INPS and INAIL", tfr: "TFR (severance accrual)", pension_disability: "ZUS pension and disability (capped)",
      accident: "Workplace accident insurance", funds: "Labour Fund and FGŚP", ppk: "PPK (employee capital plan)",
      pension_unemployment: "Pension and unemployment (capped)", health_care: "Health and long-term care (capped)",
      levies: "Insolvency and maternity levies", common_mei: "Common contingencies and MEI (capped)",
      unemployment_funds: "Unemployment, FOGASA and training (capped)", solidarity: "Solidarity contribution above the ceiling" },
    paesi: { IT: "Italy", PL: "Poland", DE: "Germany", ES: "Spain" },
    eFile: "Could not read {f}: {e}", eVuoto: "The file has no rows.", eRiga: "Row {r}: {e}", ePaese: "no rules for country «{p}»: use IT, PL, DE or ES",
    eSalario: "annual salary missing or zero", eNumero: "this is not a number: {e}",
    stampaMeta: "{s} · {d} · {oggi}",
    footer: "The same calculations as the model's Python pipeline, checked against it on every change. Not payroll or tax advice.",
    memo: "Memo", registro: "Verification register", codice: "Code",
    x_scenari: "Scenarios", x_sintesi: "Summary", x_mesi: "Months", x_costo: "One employee", xMese: "Month", xLeve: "Lever",
    preset: { Base: "Base", "Hiring freeze": "Hiring freeze", "High attrition": "High attrition", "Pay equity first": "Pay equity first" },
  },
  it: {
    brand: "Workforce Cost Model", eyebrow: "Budget del personale · FY2027", title: "Quanto costerà il personale l'anno prossimo?",
    lead: "Muovi le leve - uscite, sostituzioni, crescita, blocco delle assunzioni, aumenti, chiusura dei divari retributivi - e vedi il costo del FY2027, mese per mese, con la frase per il CFO. Sull'azienda di esempio o sul tuo personale.",
    privacy: "Il file del personale resta su questo computer: i calcoli girano in questa pagina e niente viene inviato. Puoi verificarlo staccando la rete dopo che la pagina si è aperta.",
    vistaLabel: "Vista", vScenari: "Scenari per il FY2027", vCosto: "Quanto costa un dipendente",
    step1: "Di chi è il personale", datiEsempio: "L'azienda di esempio: {n} FTE a Milano e Cracovia al 30 giugno 2026, con le uscite e il piano di crescita del modello. Carica il tuo elenco del personale per far girare gli stessi scenari.",
    datiCliente: "{f}: {n} dipendenti, {fte} FTE in {p}. Uscite e crescita qui sotto le decidi tu.",
    dropOrganico: "Il tuo elenco del personale", dropOrganicoSub: "Facoltativo · una riga per dipendente: paese, reparto, FTE, retribuzione annua, bonus",
    tornaEsempio: "Usa l'azienda di esempio", modello: "Modello:", modelloLink: "elenco del personale", modifica: "Modifica",
    colonneOk: "Trovate tutte le {n} colonne necessarie", colonneSub: "Controlla gli abbinamenti qui sotto, o cambiali.",
    colonneMancano: "Scegli la colonna per {n} voce/i in rosso.", nonPresente: "— non presente —", facoltativa: "facoltativa",
    f_country: "Paese (IT, PL, DE o ES)", f_department: "Reparto o centro di costo", f_fte: "Quota di tempo pieno (FTE)",
    f_base_salary: "Retribuzione base annua, a tempo pieno", f_bonus: "Bonus annuo",
    cUscite: "Uscite in un anno, oggi", cUsciteSub: "Quota di FTE che lascia in un anno normale.",
    cCrescita: "Crescita prevista in un anno", cCrescitaSub: "FTE nuovi oltre alle sostituzioni, in quota degli FTE di oggi.",
    step2: "Lo scenario", nome: "Nome", lUscite: "Uscite", lUsciteSub: "× il tasso di oggi: 1,3 vuol dire il 30% di uscite in più.",
    lSostituzioni: "Uscite sostituite", lSostituzioniSub: "Quota di uscite rimpiazzate, dopo il tempo di assunzione.",
    lCrescita: "Crescita", lCrescitaSub: "× il piano di crescita: 0 vuol dire nessun ruolo nuovo.",
    lBlocco: "Blocco delle assunzioni da", lBloccoSub: "Nessuna assunzione, neanche le sostituzioni, da questo mese.",
    lTth: "Tempo di assunzione", lTthSub: "Mesi tra un'uscita e l'arrivo del sostituto.", mesiN: "{n} mesi", mese1: "1 mese",
    lMeseMerito: "Aumenti da", lEquita: "Chiudere i divari retributivi da",
    lEquitaSub: "Retribuzione annua da aggiungere per paese, prima degli oneri: il tetto del costo dallo strumento sulla trasparenza retributiva.",
    nessuno: "Mai", salva: "Salva lo scenario per confrontarlo", salvato: "Salvato", nomeNuovo: "Il mio scenario",
    stampaTitolo: "Costo del personale FY2027", perCfo: "Per il CFO", mesi: "Mese per mese", mCosto: "Costo", mFte: "FTE",
    confronto: "Scenari a confronto", confrontoSub: "Lo scenario sullo schermo e quelli salvati. Gli scenari salvati restano su questo computer.",
    confrontoVuoto: "Salva uno scenario per confrontarlo con gli altri.",
    scaricaXlsx: "Scarica in Excel", stampa: "Stampa per la riunione di budget", elimina: "Elimina",
    kCosto: "Costo FY2027", kDelta: "Rispetto al {b}", kFte: "FTE medi", kChiusura: "FTE al 30 giugno 2027", kAssunzioni: "Assunzioni e loro costo",
    base26: "FY2026", baseOggi: "costo annuo di oggi",
    hPaese: "Società", hBase: "Partenza", hVolume: "Organico", hTariffa: "Retribuzioni", hEquita: "Divari", hFy27: "FY2027", hTotale: "Totale",
    hScenario: "Scenario", hCosto: "Costo FY2027", hDelta: "Variazione", hFteMedi: "FTE medi", hFteFine: "FTE a fine anno", hAssunzioni: "Assunzioni",
    hCostoAss: "Costo delle assunzioni", hEquitaC: "Divari",
    frase: "{s}: il FY2027 costa {c}, il {d} in {pm} rispetto al {b} ({cb}). L'organico {vv} {v}, le retribuzioni {rv} {r}{e}. L'anno chiude con {f} FTE, {df} in {mf} di oggi{h}.",
    fraseEquita: ", chiudere i divari retributivi aggiunge {x}", fraseAss: "; {n} assunzioni costano {x} di selezione",
    piu: "più", meno: "meno", piuFte: "più", menoFte: "meno", aggiunge: "aggiunge", toglie: "toglie", aggiungono: "aggiungono", tolgono: "tolgono",
    costoTitolo: "Quanto costa un dipendente all'azienda", costoSub: "La stessa retribuzione in quattro paesi: lordo più tutti i contributi a carico dell'azienda, per un anno del 2026.",
    kcRal: "Retribuzione base annua, a tempo pieno", kcBonus: "Bonus annuo", kcFte: "Quota di tempo pieno",
    rLordo: "Retribuzione lorda", rContributi: "Contributi a carico dell'azienda", rTotale: "Costo totale per l'azienda", rPct: "In più rispetto al lordo",
    lordo: "Retribuzione lorda", oneri: "Contributi a carico dell'azienda",
    costoNota: "Retribuzione annua contro massimali annui: un'approssimazione esatta quando la retribuzione è distribuita in modo uniforme. Italia: altri contributi INPS e INAIL al 6%, indicativi. Polonia: PPK per metà della retribuzione, convertita al cambio BCE. Germania: contributo aggiuntivo sanitario medio e assicurazione infortuni alla media 2025 delle Berufsgenossenschaften. Spagna: contratto a tempo indeterminato, tariffa infortuni per il lavoro d'ufficio. Ogni aliquota e la sua fonte sono nel registro delle verifiche.",
    voci: { social: "INPS e INAIL", tfr: "TFR", pension_disability: "ZUS pensione e invalidità (con massimale)",
      accident: "Assicurazione infortuni", funds: "Fondo del lavoro e FGŚP", ppk: "PPK (piano di accumulo)",
      pension_unemployment: "Pensione e disoccupazione (con massimale)", health_care: "Sanità e non autosufficienza (con massimale)",
      levies: "Contributi per insolvenza e maternità", common_mei: "Contingenze comuni e MEI (con massimale)",
      unemployment_funds: "Disoccupazione, FOGASA e formazione (con massimale)", solidarity: "Contributo di solidarietà oltre il massimale" },
    paesi: { IT: "Italia", PL: "Polonia", DE: "Germania", ES: "Spagna" },
    eFile: "Non riesco a leggere {f}: {e}", eVuoto: "Il file non ha righe.", eRiga: "Riga {r}: {e}", ePaese: "nessuna regola per il paese «{p}»: usa IT, PL, DE o ES",
    eSalario: "retribuzione annua mancante o pari a zero", eNumero: "non è un numero: {e}",
    stampaMeta: "{s} · {d} · {oggi}",
    footer: "Gli stessi calcoli della pipeline Python del modello, verificati a ogni modifica. Non è consulenza paghe o fiscale.",
    memo: "Memo", registro: "Registro delle verifiche", codice: "Codice",
    x_scenari: "Scenari", x_sintesi: "Sintesi", x_mesi: "Mesi", x_costo: "Un dipendente", xMese: "Mese", xLeve: "Leva",
    preset: { Base: "Base", "Hiring freeze": "Blocco assunzioni", "High attrition": "Più uscite", "Pay equity first": "Prima l'equità" },
  },
};

const CAMPI = [
  ["country", true, ["paese", "nazione", "country code", "kraj", "land", "pais", "entity country"]],
  ["department", true, ["reparto", "dipartimento", "centro di costo", "cost centre", "cost center", "funzione", "dzial", "abteilung", "departamento"]],
  ["fte", false, ["full time equivalent", "part time", "percentuale part time", "etat", "arbeitszeitanteil", "jornada"]],
  ["base_salary", true, ["salary", "base salary", "annual salary", "base_salary_eur", "ral", "retribuzione base", "retribuzione annua", "stipendio", "grundgehalt", "salario base", "wynagrodzenie"]],
  ["bonus", false, ["premio", "variable", "variabile", "bonus annuo", "premia", "pramie"]],
].map(([key, required, aliases]) => ({ key, required, aliases }));
const PAESI = { it: "IT", ita: "IT", italy: "IT", italia: "IT", pl: "PL", pol: "PL", poland: "PL", polska: "PL", polonia: "PL",
  de: "DE", deu: "DE", germany: "DE", deutschland: "DE", germania: "DE", es: "ES", esp: "ES", spain: "ES", espana: "ES", spagna: "ES" };
const COLORI = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)", "var(--s5)"];

const i18n = createI18n(UI, "en");
const t = i18n.t;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const L = () => UI[i18n.lang];
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode: fine */ } },
};
const pct = (x, d = 1) => i18n.percent(x, d).replace(/^-/, "−");
// money in the units a budget speaks: millions, thousands, euro
function M(x) {
  const a = Math.abs(x), s = x < 0 ? "−" : "";
  if (a >= 1e6) return i18n.lang === "it" ? `${s}${i18n.number(a / 1e6, 1)} mln €` : `${s}€${i18n.number(a / 1e6, 1)}M`;
  if (a >= 1e4) return i18n.lang === "it" ? `${s}${i18n.number(a / 1e3, 0)} mila €` : `${s}€${i18n.number(a / 1e3, 0)}k`;
  return i18n.money(x, 0);
}
const meseNome = (m) => new Date(Date.UTC(2026, 5 + m, 1)).toLocaleDateString(i18n.lang === "it" ? "it-IT" : "en-GB", { month: "short", year: "2-digit", timeZone: "UTC" });

// ---- the staff the scenarios run on ----------------------------------------------------------------------------
const esempio = () => ({ kind: "sample", name: "sample", cells: SAMPLE.cells, baseline: SAMPLE.baseline,
  countries: Object.keys(CFG.entities), remediation: SAMPLE.remediation, merit: CFG.merit, cost_per_hire: CFG.cost_per_hire });
let dati = esempio();
let cliente = { attrition: CFG.client.attrition, growth: CFG.client.growth };
let file = null, mapping = {};

function celle() {
  if (dati.kind === "sample") return dati.cells;
  return dati.cells.map((c) => ({ ...c, attrition: cliente.attrition, growth: cliente.growth }));
}
// a client's starting point is today's run-rate: today's FTE at today's loaded cost, for a year
function baseline() {
  if (dati.kind === "sample") return dati.baseline;
  const b = {};
  for (const c of dati.cells) { b[c.country] ||= { fte: 0, cost: 0 }; b[c.country].fte += c.fte; b[c.country].cost += c.cost; }
  return b;
}

// ---- the scenario ----------------------------------------------------------------------------------------------
function preset(s) {
  return { name: L().preset[s.name] || s.name, attrition_x: s.attrition_x, replacement: s.replacement, growth_x: s.growth_x,
    freeze_from: s.freeze_from, remediation_from: s.remediation_from, time_to_hire: CFG.time_to_hire, merit_month: CFG.merit_month,
    merit: Object.fromEntries(dati.countries.map((c) => [c, dati.merit[c] ?? CFG.client.merit[c]])),
    remediation: Object.fromEntries(dati.countries.map((c) => [c, dati.remediation[c] ?? 0])) };
}
let scenario = preset(CFG.scenarios[0]);
const chiaveSalvati = () => `strumenti.wcm.scenari.${dati.kind === "sample" ? "sample" : normalise(dati.name)}`;
let salvati = store.get(chiaveSalvati(), []);

function calcola(s) {
  const p = { months: CFG.months, merit: s.merit, merit_month: s.merit_month, time_to_hire: s.time_to_hire,
    cost_per_hire: Object.fromEntries(dati.countries.map((c) => [c, dati.cost_per_hire[c] ?? CFG.client.cost_per_hire[c]])),
    remediation: s.remediation, loaded_factor: CFG.loaded_factor };
  const f = forecast(celle(), s, p);
  const rows = summary(f, baseline(), p).sort((x, y) => CFG.countries.indexOf(x.country) - CFG.countries.indexOf(y.country));
  const tot = {};
  for (const r of rows) for (const [k, v] of Object.entries(r)) if (typeof v === "number") tot[k] = (tot[k] || 0) + v;
  return { rows, tot, mesi: monthly(f, p), opening: celle().reduce((x, c) => x + c.fte, 0) };
}

// ---- inputs on the page -------------------------------------------------------------------------------------------
const LEVE = [["l-uscite", "attrition_x", (v) => `× ${i18n.number(v, 2)}`], ["l-sostituzioni", "replacement", (v) => pct(v, 0)],
  ["l-crescita", "growth_x", (v) => `× ${i18n.number(v, 2)}`], ["l-tth", "time_to_hire", (v) => (v === 1 ? t("mese1") : t("mesiN", { n: v }))]];
function selectMesi(id, val, conNessuno) {
  $(id).innerHTML = (conNessuno ? `<option value="0">${esc(t("nessuno"))}</option>` : "") +
    Array.from({ length: CFG.months }, (_, k) => `<option value="${k + 1}" ${k + 1 === val ? "selected" : ""}>${esc(meseNome(k + 1))}</option>`).join("");
}
function scriviLeve() {
  $("nome").value = scenario.name;
  for (const [id, k, f] of LEVE) { $(id).value = scenario[k]; $(`o-${id}`).textContent = f(scenario[k]); }
  selectMesi("l-blocco", scenario.freeze_from, true);
  selectMesi("l-mese-merito", scenario.merit_month, false);
  selectMesi("l-equita", scenario.remediation_from, true);
  $("meriti").innerHTML = dati.countries.map((c) => `<label><span>${esc(L().paesi[c])} %</span><input type="number" data-merito="${c}" step="0.5" min="-10" max="20" value="${Math.round(scenario.merit[c] * 1000) / 10}" aria-label="${esc(`${t("lMeseMerito")} · ${L().paesi[c]}`)}"></label>`).join("");
  $("equita").innerHTML = dati.countries.map((c) => `<label><span>${esc(L().paesi[c])} €</span><input type="number" data-equita="${c}" step="1000" min="0" value="${Math.round(scenario.remediation[c])}" aria-label="${esc(`${t("lEquita")} · ${L().paesi[c]}`)}"></label>`).join("");
  document.querySelectorAll("[data-merito], [data-equita]").forEach((i) => i.addEventListener("input", leggiLeve));
  $("preset").innerHTML = CFG.scenarios.map((s, k) => `<button type="button" class="s-btn is-small" data-p="${k}">${esc(L().preset[s.name] || s.name)}</button>`).join("");
  $("preset").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { scenario = preset(CFG.scenarios[b.dataset.p]); scriviLeve(); mostra(); }));
}
function leggiLeve() {
  scenario = { ...scenario, name: $("nome").value || t("nomeNuovo") };
  for (const [id, k, f] of LEVE) { scenario[k] = Number($(id).value); $(`o-${id}`).textContent = f(scenario[k]); }
  scenario.freeze_from = Number($("l-blocco").value);
  scenario.merit_month = Number($("l-mese-merito").value);
  scenario.remediation_from = Number($("l-equita").value);
  scenario.merit = Object.fromEntries([...document.querySelectorAll("[data-merito]")].map((i) => [i.dataset.merito, Number(i.value) / 100]));
  scenario.remediation = Object.fromEntries([...document.querySelectorAll("[data-equita]")].map((i) => [i.dataset.equita, Number(i.value)]));
  mostra();
}
["nome", "l-uscite", "l-sostituzioni", "l-crescita", "l-tth", "l-blocco", "l-mese-merito", "l-equita"].forEach((id) => $(id).addEventListener("input", leggiLeve));

function scriviCliente() {
  $("dati-cliente").style.display = dati.kind === "client" ? "grid" : "none";
  $("c-uscite").value = cliente.attrition; $("o-c-uscite").textContent = pct(cliente.attrition, 0);
  $("c-crescita").value = cliente.growth; $("o-c-crescita").textContent = pct(cliente.growth, 1);
  const fte = dati.cells.reduce((s, c) => s + c.fte, 0);
  $("dati-sub").textContent = dati.kind === "sample" ? t("datiEsempio", { n: i18n.number(fte, 0) })
    : t("datiCliente", { f: dati.name, n: i18n.number(dati.people), fte: i18n.number(fte, 1), p: dati.countries.map((c) => L().paesi[c]).join(", ") });
}
["c-uscite", "c-crescita"].forEach((id) => $(id).addEventListener("input", () => {
  cliente = { attrition: Number($("c-uscite").value), growth: Number($("c-crescita").value) };
  scriviCliente(); mostra();
}));

// ---- a client's staff file ----------------------------------------------------------------------------------------
function messaggio(text, kind = "error") {
  const m = $("errore");
  m.textContent = text || "";
  m.className = `s-msg is-${kind}${text ? " is-shown" : ""}`;
}
const input = $("file-organico"), drop = $("drop-organico");
input.addEventListener("change", () => input.files[0] && prendiFile(input.files[0]));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("is-over"); });
drop.addEventListener("dragleave", () => drop.classList.remove("is-over"));
drop.addEventListener("drop", (e) => { e.preventDefault(); drop.classList.remove("is-over"); if (e.dataTransfer.files[0]) prendiFile(e.dataTransfer.files[0]); });

async function prendiFile(f) {
  try {
    const table = await readTable(f);
    if (!table.rows.length) throw new Error(t("eVuoto"));
    file = { name: f.name, ...table };
    $("nome-organico").textContent = `${f.name} · ${table.rows.length}`;
    drop.classList.add("is-done");
    messaggio("");
    mapping = matchColumns(file.headers, CAMPI, savedMapping("wcm", file.headers)).mapping;
    $("passo-colonne").style.display = "block";
    disegnaMappa(false);
    carica();
  } catch (e) { messaggio(t("eFile", { f: f.name, e: e.message })); }
}
const mancanti = () => CAMPI.filter((c) => c.required && !mapping[c.key]);
function disegnaMappa(apri) {
  const manca = mancanti().length;
  $("colonne-ok").textContent = t("colonneOk", { n: CAMPI.filter((c) => mapping[c.key]).length });
  $("colonne-sub").textContent = manca ? t("colonneMancano", { n: manca }) : t("colonneSub");
  const aperta = manca || apri === "forza";
  $("riepilogo-colonne").style.display = aperta ? "none" : "block";
  $("mappa").style.display = aperta ? "grid" : "none";
  $("mappa").innerHTML = CAMPI.map((c) => {
    const scelta = mapping[c.key] || "";
    return `<div class="s-map-row${c.required && !scelta ? " is-missing" : ""}"><div class="need">${esc(t(`f_${c.key}`))}
      ${c.required ? "" : `<small>${esc(t("facoltativa"))}</small>`}</div>
      <select class="s-select" data-key="${c.key}" aria-label="${esc(t(`f_${c.key}`))}"><option value="">${esc(t("nonPresente"))}</option>
      ${file.headers.map((h) => `<option ${h === scelta ? "selected" : ""}>${esc(h)}</option>`).join("")}</select></div>`;
  }).join("");
  $("mappa").querySelectorAll("select").forEach((sel) => sel.addEventListener("change", () => {
    mapping = { ...mapping, [sel.dataset.key]: sel.value };
    rememberMapping("wcm", file.headers, mapping);
    disegnaMappa("forza");
    carica();
  }));
}
$("mostra-colonne").addEventListener("click", () => disegnaMappa("forza"));

function carica() {
  if (mancanti().length) return;
  try {
    const dc = file.decimalComma;
    const rows = applyMapping(file.rows, mapping).map((r, i) => {
      const err = (e) => { throw new Error(t("eRiga", { r: i + 2, e })); };
      const num = (v) => { try { return number(v, dc); } catch { return err(t("eNumero", { e: v })); } };
      const p = String(r.country ?? "").trim(), n = normalise(p);
      const country = PAESI[n] || PAESI[n.split("_")[0]] || err(t("ePaese", { p }));
      const base = num(r.base_salary);
      if (!(base > 0)) err(t("eSalario"));
      let fte = mapping.fte ? num(r.fte) : 1;
      if (fte > 1.5) fte /= 100;
      return { country, department: String(r.department ?? "").trim() || "—", fte, base, bonus: mapping.bonus ? num(r.bonus) : 0 };
    }).filter((r) => r.fte > 0);
    const cells = cellsFromRoster(rows, R);
    const countries = CFG.countries.filter((c) => cells.some((x) => x.country === c));
    dati = { kind: "client", name: file.name, people: rows.length, cells, countries, remediation: {}, merit: CFG.client.merit,
      cost_per_hire: CFG.client.cost_per_hire };
    salvati = store.get(chiaveSalvati(), []);
    scenario = preset(CFG.scenarios[0]);
    scriviCliente(); scriviLeve(); mostra();
  } catch (e) { messaggio(e.message); }
}
$("torna-esempio").addEventListener("click", () => {
  dati = esempio(); file = null; input.value = "";
  $("nome-organico").textContent = ""; drop.classList.remove("is-done"); $("passo-colonne").style.display = "none"; messaggio("");
  salvati = store.get(chiaveSalvati(), []);
  scenario = preset(CFG.scenarios[0]);
  scriviCliente(); scriviLeve(); mostra();
});

// ---- results ------------------------------------------------------------------------------------------------------
let metrica = "cost";
const nomeBase = () => (dati.kind === "sample" ? t("base26") : t("baseOggi"));

function frase(s, r) {
  const { tot } = r, d = tot.fy27_cost / tot.fy26_cost - 1, df = tot.closing_fte - r.opening;
  return t("frase", { s: s.name, c: M(tot.fy27_cost), d: pct(Math.abs(d)), pm: d >= 0 ? t("piu") : t("meno"), b: nomeBase(), cb: M(tot.fy26_cost),
    vv: tot.bridge_volume >= 0 ? t("aggiunge") : t("toglie"), v: M(Math.abs(tot.bridge_volume)),
    rv: tot.bridge_rate >= 0 ? t("aggiungono") : t("tolgono"), r: M(Math.abs(tot.bridge_rate)),
    e: tot.fy27_remediation > 0 ? t("fraseEquita", { x: M(tot.fy27_remediation) }) : "",
    f: i18n.number(tot.closing_fte, 0), df: i18n.number(Math.abs(df), 0), mf: df >= 0 ? t("piuFte") : t("menoFte"),
    h: tot.fy27_hires >= 0.5 ? t("fraseAss", { n: i18n.number(tot.fy27_hires, 0), x: M(tot.fy27_hiring_cost) }) : "" });
}

function mostra() {
  const r = calcola(scenario), { tot } = r;
  const d = tot.fy27_cost / tot.fy26_cost - 1;
  $("kpis").innerHTML = [[t("kCosto"), M(tot.fy27_cost), ""], [t("kDelta", { b: nomeBase() }), `${d >= 0 ? "+" : "−"}${pct(Math.abs(d))}`, d > 0 ? "is-bad" : "is-good"],
    [t("kFte"), i18n.number(tot.fy27_fte, 0), ""], [t("kChiusura"), i18n.number(tot.closing_fte, 0), ""],
    [t("kAssunzioni"), `${i18n.number(tot.fy27_hires, 0)} · ${M(tot.fy27_hiring_cost)}`, ""]]
    .map(([k, v, c]) => `<div class="s-kpi ${c}"><div class="k">${esc(k)}</div><div class="v" style="font-size:26px">${v}</div></div>`).join("");
  $("frase").textContent = frase(scenario, r);
  $("stampa-meta").textContent = t("stampaMeta", { s: scenario.name, d: dati.kind === "sample" ? "Milan · Kraków" : dati.name, oggi: new Date().toLocaleDateString(i18n.lang === "it" ? "it-IT" : "en-GB") });
  const riga = (label, x, cls = "") => `<tr class="${cls}"><td class="l">${esc(label)}</td><td>${M(x.fy26_cost)}</td><td>${M(x.bridge_volume)}</td><td>${M(x.bridge_rate)}</td><td>${M(x.bridge_remediation)}</td><td><b>${M(x.fy27_cost)}</b></td></tr>`;
  $("ponte").innerHTML = `<tr><th class="l">${esc(t("hPaese"))}</th><th>${esc(t("hBase"))} (${esc(nomeBase())})</th><th>${esc(t("hVolume"))}</th><th>${esc(t("hTariffa"))}</th><th>${esc(t("hEquita"))}</th><th>${esc(t("hFy27"))}</th></tr>` +
    r.rows.map((x) => riga(dati.kind === "sample" ? CFG.entities[x.country] : L().paesi[x.country], x)).join("") + (r.rows.length > 1 ? riga(t("hTotale"), tot, "tot") : "");
  grafico(r);
  confronto(r);
}

function serie(r) {
  const all = [{ name: scenario.name, mesi: r.mesi }, ...altri().map((s) => ({ name: s.name, mesi: calcola(s).mesi }))];
  return all.slice(0, 5);
}
// the saved scenarios other than the one on screen
const altri = () => salvati.filter((s) => s.name !== scenario.name);
function grafico(r) {
  const S = serie(r), W = 720, H = 260, l = 64, b = 28, top = 12, right = 12;
  const vals = S.flatMap((s) => s.mesi.map((m) => m[metrica]));
  let lo = Math.min(...vals), hi = Math.max(...vals);
  const pad = (hi - lo) * 0.15 || hi * 0.05 || 1; lo -= pad; hi += pad;
  const x = (m) => l + ((m - 1) / (CFG.months - 1)) * (W - l - right), y = (v) => top + (1 - (v - lo) / (hi - lo)) * (H - top - b);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((k) => lo + k * (hi - lo));
  const fmt = (v) => (metrica === "cost" ? M(v) : i18n.number(v, 0));
  const grid = ticks.map((v) => `<line x1="${l}" x2="${W - right}" y1="${y(v)}" y2="${y(v)}" stroke="var(--line-soft)"/><text x="${l - 6}" y="${y(v) + 4}" text-anchor="end">${esc(fmt(v))}</text>`).join("");
  const xs = Array.from({ length: CFG.months }, (_, k) => k % 2 === 0 ? `<text x="${x(k + 1)}" y="${H - 8}" text-anchor="middle">${esc(meseNome(k + 1))}</text>` : "").join("");
  const lines = S.map((s, k) => `<polyline fill="none" stroke="${COLORI[k]}" stroke-width="${k ? 2 : 3}" ${k ? 'stroke-dasharray="6 4"' : ""} points="${s.mesi.map((m) => `${x(m.month)},${y(m[metrica])}`).join(" ")}"/>`).join("");
  $("grafico").innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("mesi"))}">${grid}${xs}${lines}</svg>`;
  $("legenda").innerHTML = S.map((s, k) => `<span><i style="background:${COLORI[k]}"></i>${esc(s.name)}</span>`).join("");
}
document.querySelectorAll("#metrica button").forEach((bt) => bt.addEventListener("click", () => {
  metrica = bt.dataset.m;
  document.querySelectorAll("#metrica button").forEach((x) => x.setAttribute("aria-pressed", String(x === bt)));
  mostra();
}));

function confronto(r) {
  const righe = [{ s: scenario, r, corrente: true }, ...salvati.map((s, i) => ({ s, r: calcola(s), i })).filter(({ s }) => s.name !== scenario.name)];
  $("confronto-sub").textContent = salvati.length ? t("confrontoSub") : t("confrontoVuoto");
  $("tab-confronto").innerHTML = `<tr><th class="l">${esc(t("hScenario"))}</th><th>${esc(t("hCosto"))}</th><th>${esc(t("hDelta"))}</th><th>${esc(t("hFteMedi"))}</th><th>${esc(t("hFteFine"))}</th><th>${esc(t("hAssunzioni"))}</th><th>${esc(t("hCostoAss"))}</th><th>${esc(t("hEquitaC"))}</th><th></th></tr>` +
    righe.map(({ s, r: x, corrente, i }) => {
      const d = x.tot.fy27_cost / x.tot.fy26_cost - 1;
      return `<tr><td class="l"><b>${esc(s.name)}</b>${corrente ? ` <span class="s-pill is-medium">●</span>` : ""}</td><td><b>${M(x.tot.fy27_cost)}</b></td><td>${d >= 0 ? "+" : "−"}${pct(Math.abs(d))}</td>
        <td>${i18n.number(x.tot.fy27_fte, 0)}</td><td>${i18n.number(x.tot.closing_fte, 0)}</td><td>${i18n.number(x.tot.fy27_hires, 0)}</td><td>${M(x.tot.fy27_hiring_cost)}</td><td>${M(x.tot.fy27_remediation)}</td>
        <td class="no-print">${corrente ? "" : `<button type="button" class="s-btn is-small" data-del="${i}">${esc(t("elimina"))}</button>`}</td></tr>`;
    }).join("");
  $("tab-confronto").querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
    salvati.splice(Number(b.dataset.del), 1); store.set(chiaveSalvati(), salvati); mostra();
  }));
}
$("salva").addEventListener("click", () => {
  salvati = [...salvati.filter((s) => s.name !== scenario.name), JSON.parse(JSON.stringify(scenario))].slice(-4);
  store.set(chiaveSalvati(), salvati);
  $("salva").textContent = `✓ ${t("salvato")}`;
  setTimeout(() => { $("salva").textContent = t("salva"); }, 1500);
  mostra();
});
$("stampa").addEventListener("click", () => print());

$("scarica-xlsx").addEventListener("click", () => {
  const tutti = [scenario, ...salvati.filter((s) => s.name !== scenario.name)];
  const ris = tutti.map((s) => ({ s, r: calcola(s) }));
  const leve = [[t("xLeve"), ...tutti.map((s) => s.name)],
    [t("lUscite"), ...tutti.map((s) => s.attrition_x)], [t("lSostituzioni"), ...tutti.map((s) => s.replacement)],
    [t("lCrescita"), ...tutti.map((s) => s.growth_x)], [t("lBlocco"), ...tutti.map((s) => (s.freeze_from ? meseNome(s.freeze_from) : t("nessuno")))],
    [t("lTth"), ...tutti.map((s) => s.time_to_hire)], [t("lMeseMerito"), ...tutti.map((s) => meseNome(s.merit_month))],
    ...dati.countries.map((c) => [`${t("lMeseMerito")} · ${L().paesi[c]} (%)`, ...tutti.map((s) => Math.round(s.merit[c] * 1000) / 10)]),
    [t("lEquita"), ...tutti.map((s) => (s.remediation_from ? meseNome(s.remediation_from) : t("nessuno")))],
    ...dati.countries.map((c) => [`${t("lEquita")} · ${L().paesi[c]} (€)`, ...tutti.map((s) => s.remediation[c] || 0)])];
  if (dati.kind === "client") leve.push([t("cUscite"), cliente.attrition], [t("cCrescita"), cliente.growth]);
  const sintesi = [[t("hScenario"), t("hPaese"), `${t("hBase")} (${nomeBase()})`, t("hVolume"), t("hTariffa"), t("hEquita"), t("hFy27"), t("hFteMedi"), t("hFteFine"), t("hAssunzioni"), t("hCostoAss")],
    ...ris.flatMap(({ s, r }) => [...r.rows.map((x) => ({ ...x, label: L().paesi[x.country] })), { ...r.tot, label: t("hTotale") }].map((x) =>
      [s.name, x.label, Math.round(x.fy26_cost), Math.round(x.bridge_volume), Math.round(x.bridge_rate), Math.round(x.bridge_remediation),
        Math.round(x.fy27_cost), Math.round(x.fy27_fte * 10) / 10, Math.round(x.closing_fte * 10) / 10, Math.round(x.fy27_hires * 10) / 10, Math.round(x.fy27_hiring_cost)]))];
  const mesi = [[t("hScenario"), t("xMese"), t("mFte"), t("mCosto")],
    ...ris.flatMap(({ s, r }) => r.mesi.map((m) => [s.name, meseNome(m.month), Math.round(m.fte * 10) / 10, Math.round(m.cost)]))];
  const frasi = ris.map(({ s, r }) => [frase(s, r)]);
  download(writeXlsx([
    { name: t("x_sintesi"), rows: sintesi, widths: [24, 14, 18, 14, 14, 12, 16, 12, 12, 12, 14] },
    { name: t("x_scenari"), rows: [...leve, [], [t("perCfo")], ...frasi], widths: [44, ...tutti.map(() => 22)] },
    { name: t("x_mesi"), rows: mesi, widths: [24, 12, 12, 16] },
    { name: t("x_costo"), rows: tabellaCosto().xlsx, widths: [46, 16, 16, 16, 16] },
  ]), `${i18n.lang === "it" ? "costo_personale" : "people_cost"}_FY2027.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
});

// ---- one employee -------------------------------------------------------------------------------------------------
function tabellaCosto() {
  const ral = Number($("k-ral").value) || 0, bonus = Number($("k-bonus").value) || 0, fte = Number($("k-fte").value) || 1;
  const gross = ral * fte + bonus, base = ral * fte;
  const per = CFG.countries.map((c) => ({ c, items: employerItems(c, gross, base, R), total: employerTotal(c, gross, base, R) }));
  const head = [t("rLordo"), ...per.map((p) => L().paesi[p.c])];
  const xlsx = [[`${t("kcRal")}: ${ral} · ${t("kcBonus")}: ${bonus} · ${t("kcFte")}: ${fte}`, ...per.map((p) => L().paesi[p.c])],
    [t("rLordo"), ...per.map(() => Math.round(gross * 100) / 100)],
    ...[...new Set(per.flatMap((p) => Object.keys(p.items)))].map((k) => [L().voci[k], ...per.map((p) => (k in p.items ? Math.round(p.items[k] * 100) / 100 : ""))]),
    [t("rTotale"), ...per.map((p) => Math.round(p.total * 100) / 100)]];
  return { per, gross, head, xlsx };
}
function mostraCosto() {
  const { per, gross } = tabellaCosto();
  $("tab-costo").innerHTML = `<tr><th class="l"></th>${per.map((p) => `<th>${esc(L().paesi[p.c])}</th>`).join("")}</tr>
    <tr><td class="l">${esc(t("rLordo"))}</td>${per.map(() => `<td>${i18n.money(gross, 0)}</td>`).join("")}</tr>
    <tr><td class="l">${esc(t("rContributi"))}</td>${per.map((p) => `<td><b>${i18n.money(p.total - gross, 0)}</b>${Object.entries(p.items).map(([k, v]) => `<div class="s-why">${esc(L().voci[k])}: ${i18n.money(v, 0)}</div>`).join("")}</td>`).join("")}</tr>
    <tr class="tot"><td class="l">${esc(t("rTotale"))}</td>${per.map((p) => `<td>${i18n.money(p.total, 0)}</td>`).join("")}</tr>
    <tr><td class="l">${esc(t("rPct"))}</td>${per.map((p) => `<td>${gross ? `+${pct(p.total / gross - 1)}` : "–"}</td>`).join("")}</tr>`;
  const W = 720, row = 40, lab = 90, H = per.length * row + 6, max = Math.max(...per.map((p) => p.total), 1), sc = (W - lab - 110) / max;
  $("grafico-costo").innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("costoTitolo"))}">${per.map((p, i) => {
    const y = i * row + 4, g = gross * sc, o = (p.total - gross) * sc;
    return `<text x="0" y="${y + 19}" style="font-weight:600;fill:var(--ink)">${esc(L().paesi[p.c])}</text>
      <rect x="${lab}" y="${y}" width="${g}" height="28" rx="5" fill="var(--line)"/>
      <rect x="${lab + g}" y="${y}" width="${o}" height="28" rx="5" fill="var(--accent)"/>
      <text x="${lab + g + o + 8}" y="${y + 19}" style="font-weight:600;fill:var(--ink)">${esc(i18n.money(p.total, 0))}</text>`;
  }).join("")}</svg>`;
  $("legenda-costo").innerHTML = `<span><i style="background:var(--line);height:12px;width:12px"></i>${esc(t("lordo"))}</span><span><i style="background:var(--accent);height:12px;width:12px"></i>${esc(t("oneri"))}</span>`;
}
["k-ral", "k-bonus", "k-fte"].forEach((id) => $(id).addEventListener("input", mostraCosto));

// ---- views --------------------------------------------------------------------------------------------------------
document.querySelectorAll("#viste button").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll("#viste button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  $("vista-scenari").style.display = b.dataset.v === "scenari" ? "block" : "none";
  $("vista-costo").style.display = b.dataset.v === "costo" ? "block" : "none";
}));
const daHash = () => document.querySelector(`#viste button[data-v="${location.hash === "#costo" ? "costo" : "scenari"}"]`).click();
addEventListener("hashchange", daHash);
if (location.hash === "#costo") daHash();

i18n.apply();
function tutto() {
  const nomeAttuale = scenario.name, preimpostato = CFG.scenarios.find((s) => Object.values(UI).some((u) => u.preset[s.name] === nomeAttuale));
  if (preimpostato) scenario.name = L().preset[preimpostato.name];
  scriviCliente(); scriviLeve(); mostra(); mostraCosto();
  if (file) disegnaMappa(false);
}
i18n.onChange(tutto);
tutto();
