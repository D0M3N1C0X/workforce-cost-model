"""
Four SVG charts for the memo, hand-written like the ones in pay-transparency-readiness-kit:
validated reference palette, light and dark steps inside each file, a <title> on every mark.
"""
from html import escape

STYLE = """<style>
  svg { --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7;
        --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --base:#0b0b0b; --up:#e34948; --down:#2a78d6; }
  @media (prefers-color-scheme: dark) {
    svg { --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781; --grid:#2c2c2a; --axis:#383835;
          --s1:#3987e5; --s2:#d95926; --s3:#199e70; --base:#ffffff; --up:#e66767; --down:#3987e5; }
  }
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--ink2); font-size: 12px; }
  .title { fill: var(--ink); font-size: 15px; font-weight: 600; }
  .muted { fill: var(--muted); font-size: 11px; }
  .val { fill: var(--ink); font-variant-numeric: tabular-nums; paint-order: stroke; stroke: var(--surface);
         stroke-width: 4px; stroke-linejoin: round; }
</style>"""


def _svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{escape(label)}">{STYLE}<rect width="{w}" height="{h}" rx="8" fill="var(--surface)"/>'
            f'{"".join(body)}</svg>\n')


def m_eur(x, d=1):
    return f"€{x / 1e6:,.{d}f}M"


def _scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) / (d1 - d0) * (r1 - r0)


def _path(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def fte_budget_actual(months, budget, actual, title):
    """months: labels; budget/actual: total FTE per month."""
    W, H, L, R, T, B = 720, 330, 60, 110, 92, 40
    lo = min(min(budget), min(actual)) * 0.98
    hi = max(max(budget), max(actual)) * 1.01
    step = 50
    lo, hi = (int(lo) // step) * step, (int(hi) // step + 1) * step
    x = _scale(0, len(months) - 1, L, W - R)
    y = _scale(lo, hi, H - B, T)
    body = [f'<text x="24" y="34" class="title">{escape(title)}</text>',
            '<text x="24" y="54">Month-end FTE, Italian and Polish entities together, July 2025 to June 2026</text>',
            f'<rect x="{L}" y="66" width="18" height="3" fill="var(--s2)"/><text x="{L + 24}" y="71">Budget</text>',
            f'<rect x="{L + 90}" y="66" width="18" height="3" fill="var(--s1)"/><text x="{L + 114}" y="71">Actual</text>']
    for v in range(lo, hi + 1, step):
        body.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/>')
        body.append(f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" class="muted">{v:,}</text>')
    for i, m in enumerate(months):
        if i % 2 == 0 or i == len(months) - 1:
            body.append(f'<text x="{x(i):.1f}" y="{H - 16}" text-anchor="middle" class="muted">{escape(m)}</text>')
    for series, colour, name in ((budget, "--s2", "Budget"), (actual, "--s1", "Actual")):
        body.append(f'<path d="{_path([(x(i), y(v)) for i, v in enumerate(series)])}" fill="none" '
                    f'stroke="var({colour})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, v in enumerate(series):
            body.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="7" fill="transparent">'
                        f'<title>{name}, {escape(months[i])}: {v:,.1f} FTE</title></circle>')
        e = len(series) - 1
        body.append(f'<circle cx="{x(e):.1f}" cy="{y(series[e]):.1f}" r="4" fill="var({colour})" '
                    f'stroke="var(--surface)" stroke-width="2"/>')
        body.append(f'<text x="{x(e) + 10:.1f}" y="{y(series[e]) + 4:.1f}" class="val">{name} {series[e]:,.0f}</text>')
    return _svg(W, H, body, title)


def variance_bridge(rows, title):
    """rows: [(entity, budget, volume, mix, rate, actual)] -> one bridge per entity."""
    W, L, R = 720, 150, 90
    band = 36
    labels = ["Volume", "Mix", "Rate"]
    H = 100 + len(rows) * (32 + band * 3 + 40) + 4
    m = max(abs(v) for r in rows for v in r[2:5])
    x = _scale(-m, m, L + 40, W - R)
    body = [f'<text x="24" y="34" class="title">{escape(title)}</text>',
            '<text x="24" y="54">FY2026 cost against budget, by effect</text>',
            f'<rect x="{L}" y="66" width="12" height="12" rx="2" fill="var(--up)"/><text x="{L + 18}" y="76">Adds cost</text>',
            f'<rect x="{L + 110}" y="66" width="12" height="12" rx="2" fill="var(--down)"/>'
            f'<text x="{L + 128}" y="76">Saves cost</text>']
    y0 = 100
    for ent, budget, volume, mix, rate, actual in rows:
        body.append(f'<text x="24" y="{y0 + 4}" class="val" style="font-weight:600">{escape(ent)}</text>')
        body.append(f'<text x="24" y="{y0 + 22}" class="muted">Budget {m_eur(budget)} → actual {m_eur(actual)}</text>')
        top = y0 + 32
        body.append(f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="{top - 4}" y2="{top + band * 3}" stroke="var(--axis)"/>')
        for i, (lab, v) in enumerate(zip(labels, (volume, mix, rate))):
            yy = top + i * band
            a, b = sorted((x(0), x(v)))
            colour = "--up" if v > 0 else "--down"
            body.append(f'<text x="{L + 32}" y="{yy + band / 2 + 4}" text-anchor="end">{lab}</text>')
            body.append(f'<rect x="{a:.1f}" y="{yy + 8}" width="{max(b - a, 1):.1f}" height="{band - 16}" rx="3" '
                        f'fill="var({colour})"><title>{escape(ent)} {lab.lower()}: {m_eur(v, 2)}</title></rect>')
            tx, anchor = (b + 6, "start") if v >= 0 else (a - 6, "end")
            body.append(f'<text x="{tx:.1f}" y="{yy + band / 2 + 4}" text-anchor="{anchor}" class="val">'
                        f'{"+" if v > 0 else "−"}{m_eur(abs(v), 2)}</text>')
        y0 = top + band * 3 + 40
    return _svg(W, H, body, title)


def scenario_costs(rows, fy26, title):
    """rows: [(scenario, people cost, hiring cost)]; fy26: FY2026 actual cost."""
    W, L, R = 720, 170, 120
    band = 40
    H = 104 + band * len(rows) + 40
    lo = min(fy26, *[r[1] for r in rows]) * 0.9
    hi = max(fy26, *[r[1] for r in rows]) * 1.02
    x = _scale(lo, hi, L, W - R)
    body = [f'<text x="24" y="34" class="title">{escape(title)}</text>',
            '<text x="24" y="54">FY2027 people cost (payroll and pay-equity remediation), both entities. '
            'The axis starts above zero.</text>',
            f'<line x1="{x(fy26):.1f}" x2="{x(fy26):.1f}" y1="84" y2="{96 + band * len(rows)}" stroke="var(--ink2)" '
            f'stroke-width="1.5"/>',
            f'<text x="{x(fy26):.1f}" y="78" text-anchor="middle" class="muted">FY2026 actual {m_eur(fy26)}</text>']
    for i, (name, cost, hiring) in enumerate(rows):
        yy = 96 + i * band
        body.append(f'<text x="{L - 12}" y="{yy + band / 2 + 4}" text-anchor="end" class="val">{escape(name)}</text>')
        w = x(cost) - L
        body.append(f'<path d="M{L},{yy + 10} H{L + w - 4} Q{L + w},{yy + 10} {L + w},{yy + 14} V{yy + band - 14} '
                    f'Q{L + w},{yy + band - 10} {L + w - 4},{yy + band - 10} H{L} Z" fill="var(--s1)">'
                    f'<title>{escape(name)}: {m_eur(cost, 2)}, change {cost / fy26 - 1:+.1%}; hiring cost {m_eur(hiring, 2)}'
                    f'</title></path>')
        change = cost / fy26 - 1
        sign = "+" if change >= 0 else "−"
        body.append(f'<text x="{L + w + 8:.1f}" y="{yy + band / 2 + 4}" class="val">{m_eur(cost)} '
                    f'({sign}{abs(change):.1%})</text>')
    return _svg(W, H, body, title)


def fte_paths(months, actual, scenarios, title):
    """actual: 12 FY2026 values; scenarios: {name: 12 FY2027 values}. Draws up to three scenarios."""
    W, H, L, R, T, B = 720, 360, 60, 150, 92, 40
    allv = actual + [v for s in scenarios.values() for v in s]
    step = 100
    lo, hi = (int(min(allv) * 0.98) // step) * step, (int(max(allv) * 1.01) // step + 1) * step
    n = len(months)
    x = _scale(0, n - 1, L, W - R)
    y = _scale(lo, hi, H - B, T)
    colours = ["--s1", "--s2", "--s3"]
    body = [f'<text x="24" y="34" class="title">{escape(title)}</text>',
            '<text x="24" y="54">Month-end FTE, both entities: FY2026 actual, then FY2027 by scenario</text>']
    legend = [("FY2026 actual", "--base")] + list(zip(scenarios, colours))
    lx = L
    for name, c in legend:
        body.append(f'<rect x="{lx}" y="66" width="18" height="3" fill="var({c})"/><text x="{lx + 24}" y="71">{escape(name)}</text>')
        lx += 36 + 7 * len(name)
    for v in range(lo, hi + 1, step):
        body.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/>')
        body.append(f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" class="muted">{v:,}</text>')
    for i, m in enumerate(months):
        if i % 3 == 0 or i == n - 1:
            body.append(f'<text x="{x(i):.1f}" y="{H - 16}" text-anchor="middle" class="muted">{escape(m)}</text>')
    body.append(f'<line x1="{x(11):.1f}" x2="{x(11):.1f}" y1="{T - 6}" y2="{H - B}" stroke="var(--axis)"/>')
    body.append(f'<path d="{_path([(x(i), y(v)) for i, v in enumerate(actual)])}" fill="none" stroke="var(--base)" stroke-width="2"/>')
    ends = []
    for (name, series), c in zip(scenarios.items(), colours):
        pts = [(x(11), y(actual[-1]))] + [(x(12 + i), y(v)) for i, v in enumerate(series)]
        body.append(f'<path d="{_path(pts)}" fill="none" stroke="var({c})" stroke-width="2" stroke-linejoin="round"/>')
        for i, v in enumerate(series):
            body.append(f'<circle cx="{x(12 + i):.1f}" cy="{y(v):.1f}" r="7" fill="transparent">'
                        f'<title>{escape(name)}, {escape(months[12 + i])}: {v:,.0f} FTE</title></circle>')
        ends.append((y(series[-1]), name, series[-1], c))
    ends.sort()
    last_y = -99
    for yy, name, v, c in ends:
        yy = max(yy, last_y + 15)
        body.append(f'<circle cx="{x(n - 1):.1f}" cy="{y(v):.1f}" r="4" fill="var({c})" stroke="var(--surface)" stroke-width="2"/>')
        body.append(f'<text x="{x(n - 1) + 10:.1f}" y="{yy + 4:.1f}" class="val">{v:,.0f}</text>')
        last_y = yy
    return _svg(W, H, body, title)
