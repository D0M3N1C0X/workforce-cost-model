"""The simulator: its inputs come from the model, its JavaScript is checked against cases computed here, and the
page keeps its promise that nothing leaves the computer."""
import json
import re

import build_web
import config as C

WEB = C.ROOT / "web"


def test_inputs_come_from_the_model(out):
    assert json.loads((WEB / "inputs.json").read_text(encoding="utf-8")) == json.loads(
        json.dumps({"cfg": build_web.cfg(), "sample": build_web.sample(out)}))


def test_javascript_cases_are_current(out, tmp_path, monkeypatch):
    committed = build_web.VECTORS.read_text(encoding="utf-8")
    monkeypatch.setattr(build_web, "VECTORS", tmp_path / "v.json")
    build_web.write_vectors(out)
    assert (tmp_path / "v.json").read_text(encoding="utf-8") == committed


def test_settings_are_restored_after_a_case():
    before = dict(C.MERIT), C.TIME_TO_HIRE
    with build_web.settings(MERIT={"IT": 0.0, "PL": 0.0}, TIME_TO_HIRE=6):
        assert C.TIME_TO_HIRE == 6
    assert (dict(C.MERIT), C.TIME_TO_HIRE) == before


def test_every_text_in_both_languages():
    page = (WEB / "index.html").read_text(encoding="utf-8")
    app = (WEB / "app.js").read_text(encoding="utf-8")
    keys = set(re.findall(r'data-i18n="(\w+)"', page)) | set(re.findall(r'data-i18n-attr="[\w-]+:(\w+)"', page))
    assert [k for k in sorted(keys) if len(re.findall(rf"\b{k}:", app)) < 2] == []


def test_the_page_loads_nothing_from_outside():
    page = (WEB / "index.html").read_text(encoding="utf-8")
    assert not re.search(r'(src|href)="https?://(?!github\.com/D0M3N1C0X/)', page)
    for js in WEB.rglob("*.js"):
        text = js.read_text(encoding="utf-8")
        assert "goatcounter" not in text.lower()
        assert not re.search(r"fetch\(\s*[\"'`]https?:", text), js.name
