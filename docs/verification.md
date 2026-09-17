# Verification register

Every rate, cap and rule the model relies on, where it comes from and how far it has been
checked. Checked on **16 and 17 September 2026**. None of this is payroll or tax advice: a real
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
