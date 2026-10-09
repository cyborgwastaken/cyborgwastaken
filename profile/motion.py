"""Spring-driven keyframe tracks for SVG (SMIL) motion graphics.

GitHub plays README SVGs through <img>: SMIL works, scripts don't. So motion is authored like a film
timeline: each Track is a value over time on one clock, springs are sampled into keyframes, and every
track compiles to an <animate>/<animateTransform> on the same duration so the whole piece stays in sync.

    tr = Track(0.0).hold(1.2).spring(1.2, 1.0, "heavy")
    svg += tr.animate("opacity", clock)
"""

import math
from dataclasses import dataclass

FPS = 30
EPS = 0.002

# (natural frequency rad/s, damping ratio): heavy = display type & camera, default = cards/panels,
# snappy = pills, pops, indicators (matches the motion-reel presets)
SPRINGS = {"heavy": (11.0, 0.96), "default": (15.0, 0.80), "snappy": (24.0, 0.62)}


def spring_curve(preset: str) -> list[tuple[float, float]]:
    """Normalized step response (progress 0→1) of a damped spring, sampled at FPS until settled."""
    w, z = SPRINGS[preset]
    wd = w * math.sqrt(1 - z * z)
    out, t = [], 0.0
    while True:
        p = 1 - math.exp(-z * w * t) * (math.cos(wd * t) + z * w / wd * math.sin(wd * t))
        out.append((t, p))
        if t > 0.1 and math.exp(-z * w * t) / math.sqrt(1 - z * z) < 0.004:
            break
        t += 1 / FPS
    out[-1] = (t, 1.0)
    return out


_CURVES = {k: spring_curve(k) for k in SPRINGS}


def settle(preset: str) -> float:
    return _CURVES[preset][-1][0]


def ease_in_out(p: float) -> float:
    return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2


Value = float | tuple[float, ...]


def lerp(a: Value, b: Value, p: float) -> Value:
    if isinstance(a, tuple):
        return tuple(x + (y - x) * p for x, y in zip(a, b))
    return a + (b - a) * p


@dataclass
class Clock:
    """One shared timeline. `dur` is the loop length; `loop=False` plays once and freezes."""
    dur: float
    loop: bool = True
    begin: float = 0.0  # negative = start part-way in (frame 0 is never empty)

    def attrs(self) -> str:
        rep = 'repeatCount="indefinite"' if self.loop else 'fill="freeze"'
        return f'dur="{self.dur:g}s" begin="{self.begin:g}s" {rep}'


class Track:
    def __init__(self, initial: Value):
        self.kf: list[tuple[float, Value]] = [(0.0, initial)]

    @property
    def value(self) -> Value:
        return self.kf[-1][1]

    @property
    def time(self) -> float:
        return self.kf[-1][0]

    def _at(self, t: float) -> None:
        if t > self.time + 1e-9:
            self.kf.append((t, self.value))

    def set(self, t: float, v: Value) -> "Track":
        """Instant jump at t (used only while the element is masked or invisible)."""
        self._at(t)
        self.kf.append((t + EPS, v))
        return self

    def spring(self, t: float, v: Value, preset: str = "default") -> "Track":
        self._at(t)
        a = self.value
        for dt, p in _CURVES[preset][1:]:
            self.kf.append((t + dt, lerp(a, v, p)))
        return self

    def ease(self, t0: float, t1: float, v: Value) -> "Track":
        self._at(t0)
        a, n = self.value, max(2, int((t1 - t0) * FPS))
        for i in range(1, n + 1):
            self.kf.append((t0 + (t1 - t0) * i / n, lerp(a, v, ease_in_out(i / n))))
        return self

    def linear(self, t0: float, t1: float, v: Value) -> "Track":
        self._at(t0)
        self.kf.append((t1, v))
        return self

    def snap(self, t: float, v: Value) -> "Track":
        """Opacity snap: reaches v within 4 frames @60fps, so it never reads as a fade."""
        return self.linear(t, t + 0.066, v)

    # ── compile ──────────────────────────────────────────────────────────────
    def _compile(self, clock: Clock) -> tuple[str, str]:
        kf = [(t, v) for t, v in self.kf if t <= clock.dur]
        if kf[-1][0] < clock.dur:
            kf.append((clock.dur, kf[-1][1]))
        # keyTimes must be non-decreasing; clamp any spring tail that ran past the next event
        times, vals, last = [], [], -1.0
        for t, v in kf:
            t = max(t, last)
            last = t
            times.append(f"{t / clock.dur:.5f}")
            vals.append(" ".join(f"{x:.2f}" for x in v) if isinstance(v, tuple) else f"{v:.3f}")
        times[0], times[-1] = "0", "1"
        return ";".join(vals), ";".join(times)

    def animate(self, attr: str, clock: Clock) -> str:
        vals, times = self._compile(clock)
        return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{times}" calcMode="linear" {clock.attrs()}/>'

    def transform(self, kind: str, clock: Clock) -> str:
        vals, times = self._compile(clock)
        return (f'<animateTransform attributeName="transform" type="{kind}" values="{vals}" keyTimes="{times}" '
                f'calcMode="linear" {clock.attrs()}/>')


# ── composable motion primitives ────────────────────────────────────────────────
_ids = [0]


def uid(prefix: str = "m") -> str:
    _ids[0] += 1
    return f"{prefix}{_ids[0]}"


def visible(clock: Clock, t_in: float, t_out: float | None = None, snap: bool = True) -> str:
    """Opacity window: snaps in at t_in and out at t_out."""
    tr = Track(0.0)
    tr.snap(t_in, 1.0) if snap else tr.set(t_in, 1.0)
    if t_out is not None:
        tr.snap(t_out, 0.0) if snap else tr.set(t_out, 0.0)
    return tr.animate("opacity", clock)


def rise(inner: str, clock: Clock, box: tuple[float, float, float, float], t_in: float,
         t_out: float | None = None, preset: str = "heavy") -> str:
    """Rise through a mask: content starts 140% of its height below the clip box, springs into
    place, and (optionally) lifts out through the top. `box` = clip rect x, y, w, h."""
    x, y, w, h = box
    off = h * 1.45
    cid = uid("rm")
    tr = Track((0.0, off)).spring(t_in, (0.0, 0.0), preset)
    if t_out is not None:
        tr.spring(t_out, (0.0, -off), "default").set(t_out + settle("default") + 0.05, (0.0, off))
    return (f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><g>{tr.transform("translate", clock)}{inner}</g></g>')


def pop(inner: str, clock: Clock, cx: float, cy: float, t_in: float, t_out: float | None = None,
        start: float = 0.6, preset: str = "snappy") -> str:
    """Grow out of a point: scale start→1 on a spring, opacity snapping in within 4 frames."""
    sc = Track(start).spring(t_in, 1.0, preset)
    if t_out is not None:
        sc.spring(t_out, start, "snappy")
    return (f'<g opacity="0">{visible(clock, t_in, (t_out + 0.08) if t_out is not None else None)}'
            f'<g transform="translate({cx:.1f} {cy:.1f})"><g>{sc.transform("scale", clock)}'
            f'<g transform="translate({-cx:.1f} {-cy:.1f})">{inner}</g></g></g></g>')


def move(inner: str, clock: Clock, track: Track) -> str:
    return f'<g>{track.transform("translate", clock)}{inner}</g>'


def draw(path_d: str, length: float, clock: Clock, t_in: float, attrs: str, preset: str = "default",
         t_out: float | None = None) -> str:
    """A stroke that draws itself on (dashoffset spring)."""
    tr = Track(length).spring(t_in, 0.0, preset)
    if t_out is not None:
        tr.set(t_out, length)
    return (f'<path d="{path_d}" fill="none" stroke-dasharray="{length:.1f} {length:.1f}" '
            f'stroke-dashoffset="{length:.1f}" {attrs}>{tr.animate("stroke-dashoffset", clock)}</path>')


def typed(text_svg_attrs: str, text: str, clock: Clock, x: float, y: float, t_in: float,
          char_w: float, cps: float = 45, t_out: float | None = None, size: float = 13) -> str:
    """Type-on: a clip rect widens one glyph at a time (discrete), like a terminal."""
    from xml.sax.saxutils import escape
    cid, n = uid("ty"), len(text)
    keys, tr = [], Track(0.0)
    for i in range(1, n + 1):
        tr.set(t_in + (i - 1) / cps, i * char_w)
    if t_out is not None:
        tr.set(t_out, 0.0)
    return (f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y - size * 1.1:.1f}" width="0" height="{size * 1.5:.1f}">'
            f'{tr.animate("width", clock)}</rect></clipPath>'
            f'<text x="{x:.1f}" y="{y:.1f}" {text_svg_attrs} clip-path="url(#{cid})">{escape(text)}</text>')
