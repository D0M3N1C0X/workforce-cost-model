"""
Every assumption the model uses, in one place, with its source. The workbook's Settings sheet is
written from this file, so the Python pipeline and the Excel model start from the same numbers.
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SOURCE_EMPLOYEES = DATA / "source" / "employees.csv"
DELIVERABLES = ROOT / "deliverables"
REPORTS = ROOT / "reports"

# The organisation analysed in hr-people-analytics (same file, same checksum as the kit).
SOURCE_REPO = "https://github.com/D0M3N1C0X/hr-people-analytics"
SOURCE_COMMIT = "201495b"
SOURCE_SHA256 = "372723241e92aa3d233c9298f8a0d2e713e72ff8f0c989e24a7bf743fc7da79c"

ENTITIES = {"IT": "IT · Milan", "PL": "PL · Kraków"}
DEPARTMENTS = ["Customer Service", "Operations", "Tech", "Sales", "Finance", "HR"]

# Fiscal years run July to June: FY2026 is the year to 30 June 2026 (the hr-people-analytics
# reporting window), FY2027 the year to 30 June 2027.
FY2026_START = date(2025, 7, 1)
FY2027_START = date(2026, 7, 1)
MONTHS = 12

# ---- Employer cost ----------------------------------------------------------------------------
# Italy
IT_IVS = 0.2381          # INPS pension contribution (IVS), employer share of 33%
IT_OTHER = 0.0600        # other INPS contributions and INAIL premium: depend on the company's INPS
                         # classification and INAIL risk rate - illustrative, set per company
TFR_DIVISOR = 13.5       # TFR accrues at annual pay / 13.5 (art. 2120 Civil Code), on base pay here

# Poland (ZUS and funds, 2026)
PL_PENSION = 0.0976      # emerytalne, capped
PL_DISABILITY = 0.0650   # rentowe, capped
PL_ACCIDENT = 0.0167     # wypadkowe, reference rate; larger payers have their own risk-based rate
PL_LABOUR_FUND = 0.0245  # Fundusz Pracy, not capped
PL_FGSP = 0.0010         # FGŚP, not capped (art. 29(1) of the act on protection of employee claims)
PL_PPK = 0.0150          # PPK basic employer contribution, not capped
PPK_PARTICIPATION = 0.5  # share of pay covered by PPK participants - illustrative
PL_CAP_PLN = 282_600     # 2026 annual limit for pension and disability contributions (30 x 9,420 PLN)
EUR_PLN = 4.2568         # ECB euro reference rate, monthly average June 2026
PL_MIN_WAGE_PLN = 4_806  # monthly minimum wage 2026 (Council of Ministers regulation, 11 Sept 2025)

# Germany (2026): employer shares. Used by the employer-cost calculator and the scenario simulator for a
# client's own staff; the sample company stays Italian and Polish.
DE_PENSION = 0.093       # Rentenversicherung, half of 18.6%, capped at DE_CAP_PENSION
DE_UNEMPLOYMENT = 0.013  # Arbeitslosenversicherung, half of 2.6%, capped at DE_CAP_PENSION
DE_HEALTH = 0.073        # Krankenversicherung, half of 14.6%, capped at DE_CAP_HEALTH
DE_HEALTH_EXTRA = 0.0145  # half of the 2.9% average additional contribution; each insurer sets its own
DE_CARE = 0.018          # Pflegeversicherung, half of 3.6% (Saxony differs), capped at DE_CAP_HEALTH
DE_INSOLVENCY = 0.0015   # Insolvenzgeldumlage (U3), on pay up to DE_CAP_PENSION
DE_U2 = 0.0044           # maternity levy (U2): varies by insurer - illustrative, on pay up to DE_CAP_PENSION
DE_ACCIDENT = 0.0108     # Berufsgenossenschaft: 2025 average of the trade associations - illustrative
DE_CAP_PENSION = 101_400  # annual contribution ceiling, pension and unemployment (8,450 a month)
DE_CAP_HEALTH = 69_750    # annual contribution ceiling, health and long-term care (5,812.50 a month)

# Spain (2026, Orden PJC/297/2026): employer shares, Régimen General, open-ended contract.
ES_COMMON = 0.2360       # contingencias comunes
ES_MEI = 0.0075          # mecanismo de equidad intergeneracional
ES_UNEMPLOYMENT = 0.0550  # desempleo, contrato indefinido (6.70% for fixed-term)
ES_FOGASA = 0.0020       # Fondo de Garantía Salarial
ES_TRAINING = 0.0060     # formación profesional
ES_ACCIDENT = 0.0150     # AT/EP: tarifa for office work (Cuadro II, letra a) - illustrative for other jobs
ES_CAP = 5_101.20 * 12   # base máxima, 5,101.20 a month
# Solidarity contribution on pay above the base máxima (art. 17.1): employer rate per monthly band.
ES_SOLIDARITY = [(5_101.20 * 12, 0.0096), (5_611.32 * 12, 0.0104), (7_651.80 * 12, 0.0122)]

# Annual target bonus by level, paid at target (same rule as pay-transparency-readiness-kit).
BONUS_TARGET = {"L1": 0.0, "L2": 0.0, "L3": 0.05, "L4": 0.08, "L5": 0.12, "L6": 0.20}

# ---- FY2026 budget (synthetic plan set at 30 June 2025) --------------------------------------
BUDGET_GROWTH = {"Customer Service": 0.02, "Operations": 0.00, "Tech": 0.06, "Sales": 0.04,
                 "Finance": 0.00, "HR": 0.00}

# ---- FY2027 forecast ---------------------------------------------------------------------------
FORECAST_GROWTH = {"Customer Service": 0.02, "Operations": 0.00, "Tech": 0.05, "Sales": 0.03,
                   "Finance": 0.00, "HR": 0.00}
MERIT = {"IT": 0.025, "PL": 0.050}   # pay review, effective from MERIT_MONTH
MERIT_MONTH = 7                      # month 7 of FY2027 = January 2027
TIME_TO_HIRE = 2                     # months between a leaver and the backfill starting (at least 1)
# External recruitment and onboarding cost per hire - illustrative, set from the company's own data.
COST_PER_HIRE = {"IT": 4000, "PL": 2500}

# Starting values the simulator offers for a client's own staff, all editable on the page - illustrative.
CLIENT_DEFAULTS = {"attrition": 0.12, "growth": 0.02,
                   "merit": {"IT": 0.025, "PL": 0.050, "DE": 0.030, "ES": 0.030},
                   "cost_per_hire": {"IT": 4000, "PL": 2500, "DE": 5000, "ES": 3000}}

# Pay-equity remediation: the upper-bound annual cost of closing flagged category gaps,
# from pay-transparency-readiness-kit (tableau/categories.csv at commit 95cdf8e).
KIT_COMMIT = "95cdf8e"
REMEDIATION = {"IT": 512_476.52, "PL": 674_086.32}

# Scenarios: attrition multiplier, replacement ratio, growth multiplier, hiring-freeze month
# (0 = none), remediation start month (0 = none).
SCENARIOS = [
    ("Base", 1.0, 0.90, 1.0, 0, 0),
    ("Hiring freeze", 1.0, 0.90, 0.0, 4, 0),
    ("High attrition", 1.3, 0.90, 1.0, 0, 0),
    ("Pay equity first", 1.0, 0.90, 1.0, 0, 7),
]
SCENARIO_FIELDS = ["attrition_x", "replacement", "growth_x", "freeze_from", "remediation_from"]
