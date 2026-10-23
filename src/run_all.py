"""
The whole model in one command:

    python src/run_all.py

roster -> FY2026 actuals and budget -> variance -> FY2027 scenarios -> Excel model -> CFO memo.
Deterministic: the same inputs give the same outputs.
"""
import time

import build_memo
import build_web
import build_workbook
import model
import report_html


def main() -> None:
    start = time.perf_counter()
    out = model.run()
    m = build_workbook.build(out)
    print(f"workbook -> deliverables/workforce_cost_model.xlsx ({len(m.checks)} reconciliation checks)")
    build_memo.write(out)
    report_html.build()
    print("memo -> reports/cfo_memo.md, reports/index.html, reports/figures/")
    build_web.write_inputs(out)
    print(f"simulator -> web/inputs.json; {build_web.write_vectors(out)} cases for the JavaScript check")
    print(f"done in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
