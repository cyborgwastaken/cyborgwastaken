"""Shared terminal-window renderer for the profile README panels.

Every panel is a self-contained SVG that matches profile/hero/hero.svg: same window chrome, palette,
scanlines and SMIL reveal animations (GitHub renders README images via <img>, which plays SMIL/CSS
animation but allows no scripts or web fonts, so everything here is plain SVG with system mono fonts).

A panel is a list of rows. Each row is a list of (text, class) spans, or a Cmd for a typed prompt.
"""

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from motion import Clock, rise, settle

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
BG, CHROME, BORDER = "#0a0e14", "#0f141c", "#1e293b"
TEXT, DIM, CYAN, DEEP = "#cbd5e1", "#64748b", "#22d3ee", "#0e7490"
GREEN, AMBER, RED, WHITE, VIOLET = "#22c55e", "#f59e0b", "#ef4444", "#f1f5f9", "#a78bfa"

CHAR_W = 7.8   # advance of a 13px system monospace glyph
LINE_H = 22
PAD_X = 36
TITLE_H = 36

STYLE = f"""
text {{ font-family: {MONO}; font-size: 13px; fill: {TEXT}; white-space: pre; }}
.dim {{ fill: {DIM}; }} .cy {{ fill: {CYAN}; }} .deep {{ fill: {DEEP}; }} .ok {{ fill: {GREEN}; font-weight: 700; }}
.warn {{ fill: {AMBER}; font-weight: 700; }} .red {{ fill: {RED}; }} .vi {{ fill: {VIOLET}; }}
.b {{ fill: {WHITE}; font-weight: 700; }} .prompt {{ fill: {CYAN}; font-weight: 700; }}
.title {{ fill: {DIM}; font-size: 12px; }} .big {{ fill: {WHITE}; font-size: 17px; font-weight: 700; }}
"""

DEFS = f"""<defs>
  <style>{STYLE}</style>
  <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
  <radialGradient id="vignette" cx="50%" cy="45%" r="75%">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/>
  </radialGradient>
  <filter id="glow" x="-10%" y="-40%" width="120%" height="180%">
    <feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""

Span = tuple[str, str]


@dataclass
class Cmd:
    """A `$ command` row that types itself in."""
    text: str
    comment: str = ""


@dataclass
class Panel:
    title: str
    width: int = 880
    rows: list = field(default_factory=list)
    step: float = 0.12      # delay between revealed rows
    start: float = 0.25
    pad_bottom: int = 22

    def add(self, *spans: Span) -> "Panel":
        self.rows.append(list(spans))
        return self

    def cmd(self, text: str, comment: str = "") -> "Panel":
        self.rows.append(Cmd(text, comment))
        return self

    def blank(self) -> "Panel":
        self.rows.append([])
        return self

    @property
    def height(self) -> int:
        return TITLE_H + 34 + (len(self.rows) - 1) * LINE_H + self.pad_bottom

    def render(self, extra: str = "", height: int | None = None) -> str:
        """Render the panel. `extra` is raw SVG drawn on top of the body (for charts etc)."""
        w, h = self.width, height or self.height
        out = [frame(w, h, self.title)]
        # one-shot clock long enough for the last row's spring to settle
        n_rows = sum(1 for r in self.rows if r and not isinstance(r, Cmd))
        typing = sum(len(r.text) / 40 + 0.1 for r in self.rows if isinstance(r, Cmd))
        clock = Clock(self.start + typing + n_rows * self.step + settle("heavy") + 0.2, loop=False)
        t, y = self.start, TITLE_H + 34
        for i, row in enumerate(self.rows):
            n_chars = len(row.text) + 3 + len(row.comment) if isinstance(row, Cmd) else sum(len(s) for s, _ in row)
            if PAD_X + (16 if isinstance(row, Cmd) else 0) + n_chars * CHAR_W > w - 16:
                raise ValueError(f"{self.title}: row {i} overflows ({n_chars} chars): {row}")
            if isinstance(row, Cmd):
                out.append(f'<text x="{PAD_X}" y="{y}" class="prompt" opacity="0">${reveal(t)}</text>')
                t = typed(out, row.text, PAD_X + 16, y, t, f"c{i}")
                if row.comment:
                    out.append(f'<text x="{PAD_X + 16 + (len(row.text) + 3) * CHAR_W:.1f}" y="{y}" class="dim" '
                               f'opacity="0">{escape(row.comment)}{reveal(t)}</text>')
                t += 0.1
            elif row:
                # rise through a mask on a heavy spring (never a plain fade)
                out.append(rise(f'<text x="{PAD_X}" y="{y}">{spans(row)}</text>', clock,
                                (PAD_X - 6, y - 15, w - PAD_X - 10, 20), t, None, "heavy"))
                t += self.step
            y += LINE_H
        out.append(extra)
        out.append(overlay(w, h))
        return "\n".join(out)


def reveal(begin: float) -> str:
    return f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'


PULSE = '<animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/>'


def spans(row: list[Span]) -> str:
    """Spans with class "pulse" keep breathing forever, so a panel is alive whenever it's seen."""
    return "".join(
        f'<tspan class="{c}">{escape(t)}{PULSE if "pulse" in c.split() else ""}</tspan>' if c else escape(t)
        for t, c in row)


def typed(out: list[str], text: str, x: float, y: float, begin: float, clip_id: str, cps: float = 40) -> float:
    """Append text that types itself in char by char; returns the time typing ends."""
    n = len(text)
    dur = max(n / cps, 0.05)
    widths = ";".join(f"{i * CHAR_W:.1f}" for i in range(n + 1))
    out.append(
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y - 14}" width="0" height="20">'
        f'<animate attributeName="width" values="{widths}" begin="{begin:.2f}s" dur="{dur:.2f}s" '
        f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
        f'<text x="{x}" y="{y}" clip-path="url(#{clip_id})">{escape(text)}</text>'
    )
    return begin + dur


def frame(w: int, h: int, title: str, chrome: bool = True) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{escape(title)}">',
        DEFS,
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
    ]
    if chrome:
        parts += [
            f'<path d="M14.5 .5h{w - 29}a14 14 0 0 1 14 14v21.5H.5V14.5a14 14 0 0 1 14-14z" fill="{CHROME}"/>',
            f'<line x1=".5" y1="{TITLE_H}" x2="{w - .5}" y2="{TITLE_H}" stroke="{BORDER}"/>',
            *(f'<circle cx="{22 + i * 20}" cy="18" r="6" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])),
            f'<text x="{w / 2}" y="22" text-anchor="middle" class="title">{escape(title)}</text>',
        ]
    return "\n".join(parts)


def overlay(w: int, h: int, top: int = TITLE_H + 1) -> str:
    return (f'<rect x="1" y="{top}" width="{w - 2}" height="{h - top - 1}" fill="url(#scan)"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#vignette)"/></svg>')


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])
