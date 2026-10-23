"""What one employee costs, in four countries: the same rules as the model for Italy and Poland, and Germany and
Spain checked by hand against their ceilings."""
import pytest

import config as C
import employer_cost as E
import model


def test_same_as_the_model_for_italy_and_poland():
    r = model.roster()
    for c, g, b, lc in zip(r["country"], r["gross"], r["base"], r["loaded_cost"], strict=True):
        assert E.total(c, g, b) == pytest.approx(lc, abs=1e-6)
    assert E.loaded_factor("IT") == model.loaded_factor("IT")


def test_germany_below_and_above_the_ceilings():
    rate_all = (C.DE_PENSION + C.DE_UNEMPLOYMENT + C.DE_HEALTH + C.DE_HEALTH_EXTRA + C.DE_CARE + C.DE_INSOLVENCY
                + C.DE_U2 + C.DE_ACCIDENT)
    assert E.total("DE", 50_000) == pytest.approx(50_000 * (1 + rate_all))
    above = E.items("DE", 200_000)
    assert above["health_care"] == pytest.approx(69_750 * (0.073 + 0.0145 + 0.018))
    assert above["pension_unemployment"] == pytest.approx(101_400 * 0.106)
    assert above["accident"] == pytest.approx(200_000 * 0.0108)        # the trade association has no ceiling here


def test_spain_ceiling_and_solidarity_bands():
    assert E.items("ES", 50_000)["solidarity"] == 0
    cap = 5_101.20 * 12
    x = E.items("ES", 100_000)
    assert x["common_mei"] == pytest.approx(cap * (0.236 + 0.0075))
    bands = ((5_611.32 - 5_101.20) * 12 * 0.0096 + (7_651.80 - 5_611.32) * 12 * 0.0104
             + (100_000 - 7_651.80 * 12) * 0.0122)
    assert x["solidarity"] == pytest.approx(bands)


def test_unknown_country_is_refused():
    with pytest.raises(ValueError):
        E.total("FR", 40_000)
