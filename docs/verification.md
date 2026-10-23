# Verification register

Every rate, cap and rule the model relies on, where it comes from and how far it has been
checked. Checked on **16 and 17 September 2026**; Germany and Spain on **23 October 2026**. None of this is payroll or tax advice: a real
budget takes its rates from the payroll provider.

**Status key**

- **Primary** - read in the official text or on the issuing body's own site.
- **Sources agree** - two or more independent secondary sources say the same.
- **Recomputed** - reproduced from the source data in this session.
- **Illustrative** - a stated assumption, not a fact. Replace it with the company's own figure.

## Italy

| # | Rule used in the model | Value | Source | Status |
|---|---|---|---|---|
| W01 | Employer share of the INPS pension contribution (IVS) for private-sector employees | 23.81% of the 33% total | [INPS contribution rates](https://www.inps.it/it/it/inps-comunica/diritti-e-obblighi-in-materia-di-sicurezza-sociale-nell-unione-e/per-le-imprese/aliquote-contributive.html); [CentroFiscale, 2026](https://centrofiscale.com/contributi-inps-busta-paga-2026/); [EPCloud](https://epcloud.it/contributo-ivs-in-busta-paga-guida-completa-al-calcolo) | Sources agree |
| W02 | Other INPS contributions and the INAIL premium | 6.0% of gross pay | They depend on the INPS classification of the company and on its INAIL risk rate | Illustrative |
| W03 | TFR accrues each year at annual pay divided by 13.5 | base pay / 13.5 | [Civil Code art. 2120, Gazzetta Ufficiale](https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.progressivo=0&art.idArticolo=2120&art.versione=5&art.codiceRedazionale=042U0262&art.dataPubblicazioneGazzetta=1942-04-04&art.idGruppo=267&art.idSottoArticolo1=10&art.idSottoArticolo=1&art.flagTipoArticolo=2) | Primary |

Art. 2120 counts every non-occasional pay element unless the collective agreement says otherwise.
The model applies the divisor to base pay only and ignores the annual
revaluation of the TFR fund (see [method](method.md#simplifications)).

## Poland (2026)

| # | Rule used in the model | Value | Source | Status |
|---|---|---|---|---|
| W04 | Employer pension (emerytalne) and disability (rentowe) contributions | 9.76% and 6.50% | [biznes.gov.pl](https://www.biznes.gov.pl/pl/portal/00274); [Poradnik Przedsiębiorcy](https://poradnikprzedsiebiorcy.pl/-skladki-zus-za-pracownikow-stopy-procentowe-i-zrodla-ich-finansowania) | Sources agree |
| W05 | Annual cap on the pension and disability contribution base: 30 times the projected average wage of 9,420 PLN | 282,600 PLN | Notice of the Minister of Family, Labour and Social Policy of 19 November 2025, as quoted by [e-prawapracownika.pl](https://e-prawapracownika.pl/10145/ograniczenie-podstawy-wymiaru-skladek-na-ubezpieczenia-spoleczne-w-2026-roku/) and [Poradnik Przedsiębiorcy](https://poradnikprzedsiebiorcy.pl/-roczne-ograniczenie-podstawy-wymiaru-skladek-na-ubezpieczenia-emerytalne-i-rentowe) | Sources agree |
| W06 | Accident contribution (wypadkowe): 1.67% is the reference rate; a payer with ten or more insured people has its own risk-based rate | 1.67% | [biznes.gov.pl](https://www.biznes.gov.pl/pl/portal/00274); [Symfonia, 2026](https://symfonia.pl/blog/firmy/male-firmy/skladki-zus-w-2026-r-dla-przedsiebiorcow-ile-wyniosa/) | Sources agree; the rate for this employer is illustrative |
| W07 | Labour Fund (Fundusz Pracy), not subject to the annual cap (art. 19(1), act on employment promotion) | 2.45% | [SD Worx](https://www.sdworx.pl/pl-pl/blog/place-benefity/fundusz-pracy); [PIT.pl](https://www.pit.pl/skladka-fundusz-pracy/) | Sources agree |
| W08 | Guaranteed Employee Benefits Fund (FGŚP), not subject to the annual cap (art. 29(1), act on the protection of employee claims) | 0.10% | [ZUS](https://www.zus.pl/en/pracujacy/fundusze-pozaubezpieczeniowe/fgsp); [Poradnik Przedsiębiorcy](https://poradnikprzedsiebiorcy.pl/-oplacanie-skladki-na-fgsp-aktualne-zasady) | Sources agree |
| W09 | PPK basic employer contribution; the 30-times cap does not apply to PPK payments | 1.5% | [mojeppk.pl, official PPK portal](https://www.mojeppk.pl/aktualnosci/limit-30-krotnosci-nie-dotyczy-wplat-ppk-1123.html) | Primary |
| W10 | Share of pay covered by PPK participants | 50% | Participation varies by employer | Illustrative |
| W11 | Monthly minimum wage from 1 January 2026 (Council of Ministers regulation of 11 September 2025) | 4,806 PLN | [Rzecznik MŚP](https://rzecznikmsp.gov.pl/placa-minimalna-wzrosnie-w-2026-r/); [Kadry w pigułce](https://kadrywpigulce.pl/minimalne-wynagrodzenie-2026-co-musi-wiedziec-kazdy-pracodawca-i-pracownik/) | Sources agree |
| W12 | Euro reference rate, monthly average for June 2026 | 4.2568 PLN per euro | [ECB Data Portal, series EXR.M.PLN.EUR.SP00.A](https://data.ecb.europa.eu/data/datasets/EXR/EXR.M.PLN.EUR.SP00.A) | Primary |

The model checks W11 on the Reconciliation sheet: no Polish full-time salary may fall below it.

## Germany (2026) - simulator and calculator only

The sample company has no German staff; these rules serve the employer-cost calculator and a client's own staff
in the [simulator](https://d0m3n1c0x.github.io/workforce-cost-model/simulator/).

| # | Rule used | Value | Source | Status |
|---|---|---|---|---|
| W22 | Contribution ceilings 2026: pension and unemployment; health and long-term care (Sozialversicherungsrechengrößen-Verordnung 2026, cabinet 8 October 2025, Bundesrat 21 November 2025) | €101,400 and €69,750 a year (€8,450 and €5,812.50 a month) | [Bundesregierung](https://www.bundesregierung.de/breg-de/aktuelles/beitragsbemessungsgrenzen-2386514); [Deutsche Rentenversicherung](https://www.deutsche-rentenversicherung.de/DRV/DE/Ueber-uns-und-Presse/Presse/Meldungen/2025/250910-sv-rechengroessen-vo-2026.html) | Primary |
| W23 | Employer shares: pension 9.3% (of 18.6%), unemployment 1.3% (of 2.6%), health 7.3% (of 14.6%), long-term care 1.8% (of 3.6%; Saxony differs) | as stated | [Techniker Krankenkasse, rates 2026](https://www.tk.de/firmenkunden/versicherung/beitraege-faq/beitragssaetze/aktuelle-beitragssaetze-in-der-sozialversicherung-2031554) | Primary (statutory insurer) |
| W24 | Average additional health contribution 2026, set by the Ministry of Health; half is paid by the employer. Each insurer sets its own | 2.9% (employer 1.45%) | [Techniker Krankenkasse](https://www.tk.de/firmenkunden/versicherung/beitraege-faq/beitragssaetze/aktuelle-beitragssaetze-in-der-sozialversicherung-2031554) | Primary; the employer's own insurer is illustrative |
| W25 | Insolvency levy (U3) and maternity levy (U2), on pay up to the pension ceiling. U2 varies by insurer; U1 applies only to employers with up to 30 staff and is left out | 0.15% and 0.44% | [Techniker Krankenkasse](https://www.tk.de/firmenkunden/versicherung/beitraege-faq/beitragssaetze/aktuelle-beitragssaetze-in-der-sozialversicherung-2031554) | U3 primary; U2 illustrative |
| W26 | Accident insurance (Berufsgenossenschaft): average contribution of the trade associations in 2025, per €100 of payroll. The real rate depends on the sector's risk class | 1.08% | [DGUV, figures for 2025](https://dguv.de/de/mediencenter/pm/zahlen-2025.jsp) | Illustrative |

## Spain (2026) - simulator and calculator only

| # | Rule used | Value | Source | Status |
|---|---|---|---|---|
| W27 | Employer shares, Régimen General: common contingencies 23.60%; intergenerational equity mechanism (MEI) 0.75% (art. 4 and 16) | as stated | [Orden PJC/297/2026, BOE 31 March 2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296) | Primary |
| W28 | Unemployment 5.50% (open-ended contract; 6.70% fixed-term), FOGASA 0.20%, vocational training 0.60%, on the same base as accidents (art. 33) | as stated | [Orden PJC/297/2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296) | Primary |
| W29 | Maximum contribution base | €5,101.20 a month | [Orden PJC/297/2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296), art. 2 and 3 | Primary |
| W30 | Solidarity contribution on pay above the maximum base, employer share by band: up to 10% above it 0.96%, from 10% to 50% above 1.04%, beyond 1.22% (art. 17.1) | as stated | [Orden PJC/297/2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296) | Primary |
| W31 | Accident and occupational disease premium (AT/EP) for office work (Cuadro II, letter a): 1.50% since 2019. Other jobs follow the activity's tariff | 1.50% | [Cuatrecasas](https://www.cuatrecasas.com/es/spain/laboral-1/art/que-trabajos-son-exclusivos-de-oficina-a-los-efectos-de-la-cotizacion-empresarial-por-accidentes-de-trabajo); [Andersen](https://es.andersen.com/criterio-preponderante-de-adecuacion-al-riesgo-existente-en-la-ocupacion-concreta-en-materia-de-cotizacion-por-accidentes-de-trabajo-y-enfermedad-profesional/) | Sources agree; illustrative for other jobs |

Annual pay is set against annual ceilings (twelve times the monthly ones), which is exact when pay is spread evenly;
Spanish minimum bases by professional group and the extra payments' prorating are not modelled.

## Pay transparency

| # | Rule used in the model | Source | Status |
|---|---|---|---|
| W13 | Employers with 250 or more workers report on the previous calendar year by 7 June 2027, then every year | Directive (EU) 2023/970, Art. 9(2); register entry V08 of [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/blob/main/docs/verification.md) | Primary |
| W14 | A category gap of at least 5% that is neither justified nor remedied within six months of reporting leads to a joint pay assessment | Art. 10(1); kit register V11 | Primary |
| W15 | Upper-bound annual cost of closing the flagged category gaps: €512,476.52 in Italy, €674,086.32 in Poland | `tableau/categories.csv` of pay-transparency-readiness-kit at commit [`95cdf8e`](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/blob/95cdf8e/tableau/categories.csv), summed by country | Recomputed |

## Company assumptions

Invented for the demonstration, set in [`src/config.py`](../src/config.py) and on the Settings
sheet, and marked there in yellow where they move the result most.

| # | Assumption | Value | Status |
|---|---|---|---|
| W16 | Target bonus by level, paid at target | 0% to 20% (as in the kit) | Illustrative |
| W17 | FY2026 budget: FTE growth by department over the year | 0% to 6% | Illustrative |
| W18 | FY2027 growth by department | 0% to 5% | Illustrative |
| W19 | Pay review from January 2027 | 2.5% Italy, 5.0% Poland | Illustrative |
| W20 | Share of leavers replaced, and months until the backfill starts | 90%, 2 months | Illustrative |
| W21 | External recruitment and onboarding cost per hire | €4,000 Italy, €2,500 Poland | Illustrative |
| W32 | Starting values offered for a client's own staff in the simulator: leavers 12% a year, growth 2%, pay review 3% in Germany and Spain, cost per hire €5,000 in Germany and €3,000 in Spain | as stated | Illustrative, editable on the page |
