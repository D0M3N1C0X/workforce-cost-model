"""
What one employee costs the employer in a year, item by item, in Italy, Poland, Germany or Spain.

The same rules as model.roster() for Italy and Poland (a test holds them equal), plus Germany and Spain for the
calculator and for a client's own staff. Annual pay against annual ceilings: a simplification of monthly
ceilings that gives the same answer when pay is spread evenly over the year. Not payroll advice.
"""
import config as C


def _capped(gross: float, cap: float) -> float:
    return min(gross, cap)


def items(country: str, gross: float, base: float | None = None) -> dict[str, float]:
    """Employer on-costs for one year of gross pay. `base` is the part of gross that is base pay (it drives the
    Italian TFR); without it, all of gross is base pay."""
    base = gross if base is None else base
    if country == "IT":
        return {"social": gross * C.IT_IVS + gross * C.IT_OTHER, "tfr": base / C.TFR_DIVISOR}
    if country == "PL":
        capped = _capped(gross, C.PL_CAP_PLN / C.EUR_PLN)
        return {"pension_disability": capped * C.PL_PENSION + capped * C.PL_DISABILITY,
                "accident": gross * C.PL_ACCIDENT, "funds": gross * C.PL_LABOUR_FUND + gross * C.PL_FGSP,
                "ppk": gross * C.PL_PPK * C.PPK_PARTICIPATION}
    if country == "DE":
        rv, kv = _capped(gross, C.DE_CAP_PENSION), _capped(gross, C.DE_CAP_HEALTH)
        return {"pension_unemployment": rv * C.DE_PENSION + rv * C.DE_UNEMPLOYMENT,
                "health_care": kv * (C.DE_HEALTH + C.DE_HEALTH_EXTRA) + kv * C.DE_CARE,
                "levies": rv * C.DE_INSOLVENCY + rv * C.DE_U2, "accident": gross * C.DE_ACCIDENT}
    if country == "ES":
        b = _capped(gross, C.ES_CAP)
        bands = C.ES_SOLIDARITY
        solidarity = 0.0
        for k, (floor, rate) in enumerate(bands):
            top = bands[k + 1][0] if k + 1 < len(bands) else float("inf")
            solidarity += max(0.0, min(gross, top) - floor) * rate
        return {"common_mei": b * C.ES_COMMON + b * C.ES_MEI,
                "unemployment_funds": b * C.ES_UNEMPLOYMENT + b * C.ES_FOGASA + b * C.ES_TRAINING,
                "accident": b * C.ES_ACCIDENT, "solidarity": solidarity}
    raise ValueError(f"no employer-cost rules for {country}")


def total(country: str, gross: float, base: float | None = None) -> float:
    """Gross pay plus every on-cost: the fully loaded annual cost."""
    on = items(country, gross, base)
    out = gross
    for v in on.values():
        out += v
    return out


COUNTRIES = ["IT", "PL", "DE", "ES"]


def loaded_factor(country: str) -> float:
    """On-costs per euro of pay added below every ceiling (as model.loaded_factor for Italy and Poland): the
    price of a pay rise or of closing a pay gap."""
    if country in ("IT", "PL"):
        import model
        return model.loaded_factor(country)
    if country == "DE":
        return 1 + (C.DE_PENSION + C.DE_UNEMPLOYMENT + C.DE_HEALTH + C.DE_HEALTH_EXTRA + C.DE_CARE + C.DE_INSOLVENCY
                    + C.DE_U2 + C.DE_ACCIDENT)
    if country == "ES":
        return 1 + C.ES_COMMON + C.ES_MEI + C.ES_UNEMPLOYMENT + C.ES_FOGASA + C.ES_TRAINING + C.ES_ACCIDENT
    raise ValueError(f"no employer-cost rules for {country}")
