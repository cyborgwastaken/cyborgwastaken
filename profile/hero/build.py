"""Builds profile/hero/hero.svg: an animated terminal boot sequence for the GitHub profile README.

Everything is drawn with SVG primitives + SMIL, so it renders identically everywhere
(GitHub serves README images through <img>, which allows SMIL/CSS animation but no scripts or web fonts).
The block-letter name is figlet "ANSI Shadow", converted to rects/paths so it never depends on a font.

    pip install pyfiglet && python profile/hero/build.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

import pyfiglet

W, H = 880, 400
PAD_X = 36
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

BG, PANEL_BORDER, TEXT, DIM = "#0a0e14", "#1e293b", "#cbd5e1", "#64748b"
CYAN, DEEP, GREEN, AMBER, RED = "#22d3ee", "#0e7490", "#22c55e", "#f59e0b", "#ef4444"

CELL_W, CELL_H = 8, 15  # figlet grid cell

out: list[str] = []


def reveal(begin: float) -> str:
    """SMIL child that flips an element from hidden to visible at `begin` seconds."""
    return f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'


def typed(text: str, x: int, y: int, begin: float, cps: float, cls: str, clip_id: str) -> float:
    """Text that types itself in, char by char, via a discrete clip-width animation. Returns end time."""
    char_w = 7.8
    n = len(text)
    dur = n / cps
    widths = ";".join(f"{i * char_w:.1f}" for i in range(n + 1))
    out.append(
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y - 14}" width="0" height="20">'
        f'<animate attributeName="width" values="{widths}" begin="{begin:.2f}s" dur="{dur:.2f}s" '
        f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
    )
    out.append(f'<text x="{x}" y="{y}" class="{cls}" clip-path="url(#{clip_id})">{escape(text)}</text>')
    return begin + dur


# ── frame ──────────────────────────────────────────────────────────────────────
out.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="Ayushman Das — backend and platform reliability engineer, founder of Arx Studios">'
)
out.append(
    f"""<defs>
  <style>
    text {{ font-family: {MONO}; font-size: 13px; fill: {TEXT}; white-space: pre; }}
    .dim {{ fill: {DIM}; }} .ok {{ fill: {GREEN}; font-weight: 700; }} .warn {{ fill: {AMBER}; font-weight: 700; }}
    .cy {{ fill: {CYAN}; }} .prompt {{ fill: {CYAN}; font-weight: 700; }} .title {{ fill: {DIM}; font-size: 12px; }}
    .sub {{ fill: {TEXT}; font-size: 14px; letter-spacing: .4px; }}
  </style>
  <linearGradient id="ink" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#67e8f9"/><stop offset=".55" stop-color="{CYAN}"/><stop offset="1" stop-color="#0891b2"/>
  </linearGradient>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#ffffff" opacity=".035"/>
  </pattern>
  <radialGradient id="vignette" cx="50%" cy="45%" r="75%">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/>
  </radialGradient>
</defs>"""
)
out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{PANEL_BORDER}"/>')
# title bar
out.append(f'<path d="M14.5 .5h{W - 29}a14 14 0 0 1 14 14v21.5H.5V14.5a14 14 0 0 1 14-14z" fill="#0f141c"/>')
out.append(f'<line x1=".5" y1="36" x2="{W - .5}" y2="36" stroke="{PANEL_BORDER}"/>')
for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    out.append(f'<circle cx="{22 + i * 20}" cy="18" r="6" fill="{c}"/>')
out.append(f'<text x="{W / 2}" y="22" text-anchor="middle" class="title">visitor@ayuxcyb.fun — ssh — 88×24</text>')

# ── boot log ───────────────────────────────────────────────────────────────────
y = 70
t = typed("ssh visitor@ayuxcyb.fun", PAD_X + 16, y, 0.4, 26, "", "c0")
out.append(f'<text x="{PAD_X}" y="{y}" class="prompt">$</text>')

boot = [
    ("ok", "Mounted /home/ayushman", "B.Tech CS&E @ VIT Bhopal (8.80) · BS Data Science @ IIT Madras"),
    ("ok", "Started observability.service", "prometheus · distributed tracing · structured logs · alerting"),
    ("ok", "Started arx-studios.service", "compilers · games · web products"),
    ("warn", "coffee.service", "running low, consider restarting"),
    ("ok", "Reached target production.target", ""),
]
t += 0.35
for kind, unit, note in boot:
    y += 22
    tag, cls = ("  OK  ", "ok") if kind == "ok" else (" WARN ", "warn")
    note_svg = f'<tspan class="dim">  {escape(note)}</tspan>' if note else ""
    out.append(
        f'<text x="{PAD_X}" y="{y}" opacity="0"><tspan class="dim">[</tspan><tspan class="{cls}">{tag}</tspan>'
        f'<tspan class="dim">]</tspan> {escape(unit)}{note_svg}{reveal(t)}</text>'
    )
    t += 0.32

# ── figlet name, drawn as geometry ─────────────────────────────────────────────
art = pyfiglet.figlet_format("AYUSHMAN DAS", font="ansi_shadow", width=400).rstrip("\n").splitlines()
art = [row for row in art if row.strip()]
cols = max(len(r) for r in art)
ox = (W - cols * CELL_W) / 2
oy = y + 30
name_begin = t + 0.25

blocks, shadow = [], []
for r, row in enumerate(art):
    for c, ch in enumerate(row):
        x0, y0 = ox + c * CELL_W, oy + r * CELL_H
        cx, cy = x0 + CELL_W / 2, y0 + CELL_H / 2
        if ch == "█":
            blocks.append(f"M{x0:.1f} {y0:.1f}h{CELL_W}v{CELL_H}h-{CELL_W}z")
        elif ch in "═║╗╝╚╔":
            segs = {
                "═": [(x0, cy, x0 + CELL_W, cy)],
                "║": [(cx, y0, cx, y0 + CELL_H)],
                "╗": [(x0, cy, cx, cy), (cx, cy, cx, y0 + CELL_H)],
                "╝": [(x0, cy, cx, cy), (cx, cy, cx, y0)],
                "╚": [(x0 + CELL_W, cy, cx, cy), (cx, cy, cx, y0)],
                "╔": [(x0 + CELL_W, cy, cx, cy), (cx, cy, cx, y0 + CELL_H)],
            }[ch]
            shadow += [f"M{a:.1f} {b:.1f}L{c2:.1f} {d:.1f}" for a, b, c2, d in segs]

name_w, name_h = cols * CELL_W, len(art) * CELL_H

# rows wipe in left→right, staggered, like a CRT drawing the frame
out.append('<clipPath id="wipe">')
for r in range(len(art)):
    begin = name_begin + r * 0.07
    out.append(
        f'<rect x="{ox}" y="{oy + r * CELL_H}" width="0" height="{CELL_H + .5}">'
        f'<animate attributeName="width" from="0" to="{name_w}" begin="{begin:.2f}s" dur="0.55s" '
        f'fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/></rect>'
    )
out.append("</clipPath>")

name_paths = (
    f'<path d="{"".join(shadow)}" stroke="{DEEP}" stroke-width="1.6" fill="none" stroke-linecap="square"/>'
    f'<path d="{"".join(blocks)}" fill="url(#ink)"/>'
)
out.append(f'<g clip-path="url(#wipe)" filter="url(#glow)">{name_paths}</g>')

# chromatic-aberration glitch: two tinted copies that flicker every ~7s
glitch_start = name_begin + 1.1
for dx, col in ((-3, RED), (3, CYAN)):
    out.append(
        f'<g opacity="0" transform="translate({dx} 0)" style="mix-blend-mode:screen">'
        f'<path d="{"".join(blocks)}" fill="{col}"/>'
        f'<animate attributeName="opacity" begin="{glitch_start:.2f}s" dur="7s" repeatCount="indefinite" '
        f'values="0;.55;0;.4;0;0" keyTimes="0;.012;.025;.035;.05;1" calcMode="discrete"/></g>'
    )
# a scan band that sweeps the name during each glitch
out.append(
    f'<rect x="{ox - 6}" y="{oy}" width="{name_w + 12}" height="3" fill="{CYAN}" opacity="0">'
    f'<animate attributeName="opacity" begin="{glitch_start:.2f}s" dur="7s" repeatCount="indefinite" '
    f'values="0;.5;0;0" keyTimes="0;.01;.06;1"/>'
    f'<animate attributeName="y" begin="{glitch_start:.2f}s" dur="7s" repeatCount="indefinite" '
    f'values="{oy};{oy + name_h};{oy + name_h}" keyTimes="0;.06;1"/></rect>'
)

# ── tagline + live prompt ──────────────────────────────────────────────────────
y = oy + name_h + 34
t = name_begin + 1.0
sub = "backend & platform reliability engineer  ·  founder @ arx studios  ·  bhubaneswar, in"
out.append(f'<text x="{W / 2}" y="{y}" text-anchor="middle" class="sub" opacity="0">{escape(sub)}{reveal(t)}</text>')

y += 34
t += 0.5
out.append(f'<text x="{PAD_X}" y="{y}" class="prompt" opacity="0">${reveal(t)}</text>')
t2 = typed("cat ./README.md   # scroll down ↓", PAD_X + 16, y, t + 0.3, 22, "dim", "c1")
cursor_x = PAD_X + 16 + len("cat ./README.md   # scroll down ↓") * 7.8 + 4
out.append(
    f'<rect x="{cursor_x:.1f}" y="{y - 12}" width="8" height="15" fill="{CYAN}" opacity="0">'
    f'<animate attributeName="opacity" values="1;0" dur="1.05s" begin="{t2:.2f}s" '
    f'repeatCount="indefinite" calcMode="discrete"/></rect>'
)

# ── CRT overlays ───────────────────────────────────────────────────────────────
out.append(f'<rect x="1" y="37" width="{W - 2}" height="{H - 38}" fill="url(#scan)" pointer-events="none"/>')
out.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#vignette)" pointer-events="none"/>')
out.append("</svg>")

assert y + 30 <= H, f"content overflows: {y}"
Path(__file__).with_name("hero.svg").write_text("\n".join(out), encoding="utf-8")
print(f"wrote hero.svg ({cols} cols, last line y={y})")
