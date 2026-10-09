"""Builds profile/telemetry/telemetry.svg: a self-hosted stats dashboard for the profile README.

Pulls the contribution calendar, repos, stars and languages (personal + arx-studios) from the GitHub
GraphQL API, then draws them in the same terminal style as the hero. Runs daily in telemetry.yml.

    GH_TOKEN=... python profile/telemetry/build.py
"""

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER, ORG = "cyborgwastaken", "arx-studios"
OUT = Path(__file__).with_name("telemetry.svg")

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
BG, BORDER, TEXT, DIM, CYAN = "#0a0e14", "#1e293b", "#cbd5e1", "#64748b", "#22d3ee"
HEAT = ["#111827", "#083344", "#0e7490", "#06b6d4", "#67e8f9"]

REPO_FIELDS = """totalCount nodes { stargazerCount isFork
  languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }"""
QUERY = f"""
query {{
  user(login: "{USER}") {{
    followers {{ totalCount }}
    contributionsCollection {{ contributionCalendar {{ totalContributions
      weeks {{ contributionDays {{ date contributionCount weekday }} }} }} }}
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{ {REPO_FIELDS} }}
  }}
  organization(login: "{ORG}") {{ repositories(privacy: PUBLIC, first: 100) {{ {REPO_FIELDS} }} }}
}}"""


def fetch() -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]


def streaks(days: list[dict]) -> tuple[int, int]:
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
        elif i == 0:  # today may simply not have a commit yet
            continue
        else:
            break
    return current, best


def main() -> None:
    data = fetch()
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, best = streaks(days)

    repos = [r for r in data["user"]["repositories"]["nodes"] + data["organization"]["repositories"]["nodes"]
             if not r["isFork"]]
    stars = sum(r["stargazerCount"] for r in repos)
    langs: dict[str, list] = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            if name in ("ShaderLab", "HLSL", "Wolfram Language", "Mathematica"):  # Unity/template noise
                continue
            langs.setdefault(name, [0, e["node"]["color"] or DIM])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:7]
    total_bytes = sum(v[0] for _, v in top) or 1

    W, H = 880, 338
    s: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="GitHub telemetry: {cal["totalContributions"]} contributions in the last year">',
        f"""<style>
  text {{ font-family: {MONO}; fill: {TEXT}; }}
  .k {{ font-size: 11px; fill: {DIM}; letter-spacing: 1.2px; }}
  .v {{ font-size: 26px; font-weight: 700; fill: #f1f5f9; }}
  .u {{ font-size: 12px; fill: {CYAN}; }}
  .lg {{ font-size: 11.5px; fill: {TEXT}; }}
  .cell {{ opacity: 0; animation: pop .35s ease-out forwards; }}
  @keyframes pop {{ from {{ opacity: 0; transform: translateY(-4px); }} to {{ opacity: 1; transform: none; }} }}
  .bar {{ transform-origin: left; transform: scaleX(0); animation: grow 1.1s cubic-bezier(.2,.7,.3,1) .4s forwards; }}
  @keyframes grow {{ to {{ transform: scaleX(1); }} }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ opacity: .25; }} }}
</style>""",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<circle cx="28" cy="27" r="4.5" fill="#22c55e" class="pulse"/>',
        f'<text x="42" y="31" style="font-size:12.5px"><tspan fill="{CYAN}" font-weight="700">telemetry</tspan>'
        f'<tspan fill="{DIM}">  ·  github.com/{USER} + github.com/{ORG}  ·  refreshed {dt.date.today():%d %b %Y}</tspan></text>',
        f'<line x1="20" y1="46" x2="{W - 20}" y2="46" stroke="{BORDER}"/>',
    ]

    # stat tiles
    tiles = [
        ("CONTRIBUTIONS", f"{cal['totalContributions']:,}", "last 12 months"),
        ("CURRENT STREAK", f"{current}", f"days · best {best}"),
        ("PUBLIC REPOS", f"{len(repos)}", f"{data['user']['repositories']['totalCount']} personal + "
                                         f"{data['organization']['repositories']['totalCount']} arx"),
        ("STARS", f"{stars}", f"{data['user']['followers']['totalCount']} followers"),
    ]
    tw = (W - 40 - 3 * 14) / 4
    for i, (k, v, u) in enumerate(tiles):
        x = 20 + i * (tw + 14)
        s.append(f'<rect x="{x:.1f}" y="60" width="{tw:.1f}" height="78" rx="9" fill="#0f141c" stroke="{BORDER}"/>')
        s.append(f'<text x="{x + 16:.1f}" y="82" class="k">{k}</text>')
        s.append(f'<text x="{x + 16:.1f}" y="113" class="v">{escape(v)}</text>')
        s.append(f'<text x="{x + 16:.1f}" y="129" class="u">{escape(u)}</text>')

    # contribution heatmap, revealed column by column
    max_c = max((d["contributionCount"] for d in days), default=0) or 1
    cell, gap, hx, hy = 12, 3, 20, 158
    cols = weeks[-58:] if len(weeks) > 58 else weeks
    hx = (W - len(cols) * (cell + gap) + gap) / 2
    for ci, wk in enumerate(cols):
        for d in wk["contributionDays"]:
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / max_c))
            x, y = hx + ci * (cell + gap), hy + d["weekday"] * (cell + gap)
            s.append(f'<rect class="cell" style="animation-delay:{ci * 0.018:.3f}s" x="{x:.1f}" y="{y}" '
                     f'width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lvl]}"><title>{d["date"]}: {c}</title></rect>')

    # language bar + legend
    by = hy + 7 * (cell + gap) + 18
    bx, bw = 20, W - 40
    s.append(f'<clipPath id="barclip"><rect x="{bx}" y="{by}" width="{bw}" height="8" rx="4"/></clipPath>')
    s.append(f'<g clip-path="url(#barclip)"><g class="bar">')
    x = bx
    for name, (size, color) in top:
        w = bw * size / total_bytes
        s.append(f'<rect x="{x:.1f}" y="{by}" width="{w + .5:.1f}" height="8" fill="{color}"/>')
        x += w
    s.append("</g></g>")
    lx, ly = bx, by + 28
    for name, (size, color) in top:
        label = f"{name} {100 * size / total_bytes:.1f}%"
        s.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="4.5" fill="{color}"/>')
        s.append(f'<text x="{lx + 15}" y="{ly}" class="lg">{escape(label)}</text>')
        lx += 15 + len(label) * 7.1 + 22

    s.append("</svg>")
    OUT.write_text("\n".join(s), encoding="utf-8")
    print(f"wrote {OUT.name}: {cal['totalContributions']} contributions, {len(repos)} repos, {stars} stars")


if __name__ == "__main__":
    main()
