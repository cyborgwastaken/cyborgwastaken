"""Builds profile/reel/reel.svg: a looping 32 s showreel (8 shots × 4 s) inside a terminal-window player.

Each shot: masked type rising on heavy springs (left), a project-specific motion diagram growing in
on a default spring (right), all on one clock with a scrubber that fills per shot. The loop never
stops, so the panel is alive whenever someone scrolls to it.

    python profile/reel/build.py
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

import chess.svg

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from motion import Clock, Track, draw, pop, rise, settle, typed, uid, visible  # noqa: E402
from term import BORDER, CYAN, DEEP, DIM, TEXT, WHITE, frame, overlay, wrap  # noqa: E402

W, H = 880, 476
SHOT, N = 4.0, 8
CLK = Clock(SHOT * N, loop=True, begin=-0.9)  # start 0.9 s in, so frame 0 is never empty
DX, DY = 440, 62                               # diagram origin
NODE_FILL, LINE, PALE = "#0f1a24", "#334155", "#94a3b8"


# ── tiny drawing kit (all local to the diagram box) ──────────────────────────────
def txt(x, y, s, size=12, fill=TEXT, weight=400, anchor="start", extra=""):
    # inline style, not presentation attributes: the panel's `text {}` CSS rule would override those
    return (f'<text x="{x:.1f}" y="{y:.1f}" style="font-size:{size}px;fill:{fill};font-weight:{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def node(x, y, w, h, label, size=12, fill=CYAN):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{NODE_FILL}" stroke="{DEEP}"/>'
            + txt(x + w / 2, y + h / 2 + size * 0.36, label, size, fill, anchor="middle"))


def flash(x, y, w, h, t, hold=0.35):
    """A highlight ring that snaps on when something arrives, then eases off."""
    tr = Track(0.0).snap(t, 1.0).linear(t + hold, t + hold + 0.35, 0.0)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{CYAN}" stroke-width="2" '
            f'opacity="0">{tr.animate("opacity", CLK)}</rect>')


def chip(cx, cy, label, t_in, t_out=None, size=11, fill=CYAN, bg="#082f3a"):
    w = len(label) * size * 0.62 + 16
    body = (f'<rect x="{cx - w / 2:.1f}" y="{cy - 11}" width="{w:.1f}" height="22" rx="11" fill="{bg}" stroke="{fill}"/>'
            + txt(cx, cy + size * 0.36, label, size, fill, 700, "middle"))
    return pop(body, CLK, cx, cy, t_in, t_out)


def packet(points, times, t_show, t_hide, color=CYAN, size=10):
    """A square that eases between waypoints: points[i] → points[i+1] during times[i]."""
    tr = Track(points[0])
    for (t0, t1), p in zip(times, points[1:]):
        tr.ease(t0, t1, p)
    s = size / 2
    return (f'<g opacity="0">{visible(CLK, t_show, t_hide)}<g>{tr.transform("translate", CLK)}'
            f'<rect x="{-s}" y="{-s}" width="{size}" height="{size}" rx="2" fill="{color}"/></g></g>')


def line(x1, y1, x2, y2, t, color=LINE, width=1.5):
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return draw(f"M{x1} {y1}L{x2} {y2}", length, CLK, t, f'stroke="{color}" stroke-width="{width}"')


def bar(x, y, w, h, t, frac, preset="heavy", start=0.0, color=CYAN):
    tr = Track(w * start).spring(t, w * frac, preset)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="#1e293b"/>'
            f'<rect x="{x}" y="{y}" width="{w * start:.1f}" height="{h}" rx="{h / 2}" fill="{color}">'
            f'{tr.animate("width", CLK)}</rect>')


# ── shot diagrams. S = shot start (s); coordinates are local to the 408×320 box ──
def d_axl(S):
    V, R, RD, PG = (39, 155), (164, 155), (322, 82), (322, 237)
    g = [line(78, 155, 118, 155, S + .3), line(210, 148, 262, 88, S + .38), line(322, 104, 322, 215, S + .46)]
    nodes = (node(0, 135, 78, 40, "visitor") + node(118, 135, 92, 40, "/[code]")
             + node(262, 60, 120, 44, "redis") + node(262, 215, 120, 44, "postgres"))
    # request A: cache hit
    g += [packet([V, R, RD], [(S + .5, S + .78), (S + .78, S + 1.06)], S + .5, S + 1.1),
          flash(262, 60, 120, 44, S + 1.06), chip(322, 40, "HIT", S + 1.06, S + 1.6),
          packet([RD, R, V], [(S + 1.1, S + 1.32), (S + 1.32, S + 1.54)], S + 1.1, S + 1.58, WHITE),
          chip(39, 112, "302", S + 1.54, S + 1.95)]
    # request B: miss → postgres → populate cache
    g += [packet([V, R, RD], [(S + 1.62, S + 1.9), (S + 1.9, S + 2.18)], S + 1.62, S + 2.2),
          chip(322, 40, "MISS", S + 2.18, S + 2.62),
          packet([RD, PG], [(S + 2.22, S + 2.48)], S + 2.2, S + 2.5),
          flash(262, 215, 120, 44, S + 2.48),
          packet([PG, RD], [(S + 2.52, S + 2.76)], S + 2.5, S + 2.8, WHITE),
          chip(354, 160, "populate", S + 2.56, S + 3.1),
          packet([RD, R, V], [(S + 2.8, S + 3.02), (S + 3.02, S + 3.24)], S + 2.8, S + 3.28, WHITE),
          chip(39, 112, "302", S + 3.24)]
    # packets sit behind the boxes: they read in transit, the flash marks each arrival
    packets = [x for x in g if 'height="10" rx="2"' in x]
    g = [x for x in g if x not in packets]
    g = g[:3] + packets + [nodes] + g[3:]
    # click counter: INCR runs after the response, never on the redirect's path
    g.append(txt(0, 304, "after():", 12, DIM) + txt(66, 304, "INCR clicks:abc123 =", 12, TEXT))
    for v, (a, b) in enumerate([(S + .12, S + 1.54), (S + 1.54, S + 3.24), (S + 3.24, None)]):
        g.append(rise(txt(232, 304, str(v), 12, CYAN, 700), CLK, (228, 290, 30, 19), a, b, "snappy"))
    return "".join(g)


def d_chronovault(S):
    g = []
    slots = [(150 + (i % 3) * 58, 40 + (i // 3) * 44) for i in range(6)]
    g.append(txt(150, 28, "ipfs", 11, DIM))
    for x, y in slots:
        g.append(f'<rect x="{x}" y="{y}" width="44" height="30" rx="5" fill="none" stroke="{LINE}" stroke-dasharray="3 3"/>')
    # the file, then its encryption
    file_svg = (f'<path d="M10 110h40l16 16v56h-56z" fill="{NODE_FILL}" stroke="{PALE}"/>'
                f'<path d="M50 110v16h16" fill="none" stroke="{PALE}"/>' + txt(38, 202, "report.pdf", 11, PALE, anchor="middle"))
    shrink = Track(1.0).spring(S + 1.0, 0.5, "snappy")
    g.append(f'<g opacity="0">{visible(CLK, S + .15, S + 1.12)}<g transform="translate(38 146)"><g>'
             f'{shrink.transform("scale", CLK)}<g transform="translate(-38 -146)">{file_svg}</g></g></g></g>')
    lock = (f'<rect x="27" y="144" width="22" height="16" rx="3" fill="{CYAN}"/>'
            f'<path d="M31 144v-5a7 7 0 0 1 14 0v5" fill="none" stroke="{CYAN}" stroke-width="2.5"/>')
    g.append(pop(lock, CLK, 38, 150, S + .55, S + 1.0))
    g.append(chip(38, 226, "AES-256-GCM", S + .6, S + 1.6))
    # shards fly into IPFS slots
    for i, (x, y) in enumerate(slots):
        t = S + 1.05 + i * .06
        tr = Track((16.0, 131.0)).spring(t, (float(x), float(y)), "default")
        g.append(f'<g opacity="0">{visible(CLK, t)}<g>{tr.transform("translate", CLK)}'
                 f'<rect width="44" height="30" rx="5" fill="#0b3a48" stroke="{CYAN}"/>'
                 f'{txt(22, 19, f"#{i}", 10, CYAN, 700, "middle")}</g></g>')
    # merkle tree builds upward
    cols = [172 + c * 58 for c in range(3)]
    leaves = [(cols[i % 3] + (-11 if i < 3 else 11), 152) for i in range(6)]
    mids = [(x, 198) for x in cols]
    root = (230, 246)
    for i, ((sx, sy), (lx, ly)) in enumerate(zip(slots, leaves)):
        g.insert(1, line(sx + 22, sy + 30, lx, ly, S + 1.6 + i * .03, LINE, 1))  # behind the shards
    for i, (lx, ly) in enumerate(leaves):
        mx, my = mids[i % 3]
        g.append(line(lx, ly, mx, my, S + 1.9, DEEP, 1.5))
    for mx, my in mids:
        g.append(line(mx, my, *root, S + 2.25, DEEP, 1.5))
    for i, (x, y) in enumerate(leaves):
        g.append(pop(f'<circle cx="{x}" cy="{y}" r="4" fill="{CYAN}"/>', CLK, x, y, S + 1.82 + i * .03))
    for x, y in mids:
        g.append(pop(f'<circle cx="{x}" cy="{y}" r="5" fill="{CYAN}"/>', CLK, x, y, S + 2.2))
    g.append(pop(f'<circle cx="{root[0]}" cy="{root[1]}" r="7" fill="{CYAN}"/>', CLK, *root, S + 2.55))
    g.append(chip(230, 276, "root 0x9f3a…c41e", S + 2.6))
    g.append(line(237, 246, 330, 246, S + 2.8, DEEP, 1.5))
    g.append(pop(node(330, 230, 78, 32, "sepolia", 11), CLK, 369, 246, S + 2.98))
    return "".join(g)


ANX_SRC = ["int binarySearch(int[] arr, int target) {", "    int lo = 0;", "    int hi = arr.length - 1;",
           "    while (lo <= hi) {", "        int mid = lo + (hi - lo) / 2;"]
ANX_IR = ["define i32 @binarySearch(ptr %arr, i32 %target) {", "entry:", "  %lo = alloca i32, align 4",
          "  br label %while.cond"]


def code_box(y, h, name):
    return (f'<rect x="0" y="{y}" width="408" height="{h}" rx="8" fill="#0b1219" stroke="{BORDER}"/>'
            + txt(12, y + 17, name, 11, DIM))


def d_anx(S):
    g = [code_box(0, 122, "binary_search.nx")]
    for i, ln in enumerate(ANX_SRC):
        g.append(typed(f'style="font-size:11.5px;fill:{TEXT}"', ln, CLK, 12, 40 + i * 17, S + .3 + i * .2, 6.95, cps=110, size=11.5))
    g.append(txt(0, 145, "$", 12, CYAN, 700))
    g.append(typed(f'style="font-size:12px;fill:{TEXT}"', "anx build --native", CLK, 14, 145, S + 1.4, 7.2, cps=50, size=12))
    g.append(code_box(158, 96, "binarySearch.ll"))
    for i, ln in enumerate(ANX_IR):
        y = 196 + i * 16
        g.append(rise(txt(12, y, ln, 11.5, CYAN if i == 0 else TEXT), CLK, (8, y - 12, 396, 16), S + 1.85 + i * .1, None, "default"))
    for i, (label, t) in enumerate([("interpreter", S + 2.45), ("native", S + 2.6)]):
        y = 274 + i * 26
        g.append(txt(0, y + 8, label, 11.5, PALE) + bar(96, y, 236, 8, t, 1.0))
        g.append(rise(txt(344, y + 8, "20/20 ✓", 11.5, CYAN, 700), CLK, (340, y - 6, 68, 18), t + .35, None, "snappy"))
    return "".join(g)


ARX_SRC = ["int[] my_array = {10, 20, 30};", "for (int i = 0; i < my_array.length; i++) {",
           "    my_array[i] = my_array[i] * 2;", "    print(my_array[i]);", "}"]
ARX_C = ["int my_array[] = {10, 20, 30};", "for (int i = 0; i < 3; i++) {",
         "    my_array[i] = my_array[i] * 2;", '    printf("%d\\n", my_array[i]);', "}"]


def d_arxcy(S):
    g = [code_box(0, 122, "test.arx")]
    sel = Track((0.0, 0.0))
    for i in range(5):
        sel.spring(S + .55 + i * .42, (0.0, i * 17.0), "snappy")
    g.append(f'<g opacity="0">{visible(CLK, S + .55, S + 2.95)}<g>{sel.transform("translate", CLK)}'
             f'<rect x="6" y="28" width="396" height="16" rx="3" fill="{CYAN}" opacity=".16"/>'
             f'<rect x="6" y="28" width="2.5" height="16" fill="{CYAN}"/></g></g>')
    for i, ln in enumerate(ARX_SRC):
        g.append(txt(14, 40 + i * 17, ln, 11.5, TEXT))
    g.append(txt(0, 145, "$", 12, CYAN, 700) + typed(f'style="font-size:12px;fill:{TEXT}"', "arxcy test.arx -o test.c", CLK,
                                                      14, 145, S + .3, 7.2, cps=60, size=12))
    g.append(code_box(158, 122, "test.c"))
    for i, ln in enumerate(ARX_C):
        y = 198 + i * 17
        g.append(rise(txt(14, y, ln, 11.5, TEXT), CLK, (8, y - 12, 396, 16), S + .7 + i * .42, None, "default"))
    g.append(chip(204, 304, "gcc test.c  ✓", S + 2.85))
    return "".join(g)


AGENTS = [("DUELIST", "JETT", (.9, .55, .4)), ("CONTROLLER", "OMEN", (.5, .85, .5)), ("INITIATOR", "SOVA", (.6, .5, .9)),
          ("SENTINEL", "KILLJOY", (.4, .7, .8)), ("DUELIST", "REYNA", (.95, .4, .35)), ("SENTINEL", "SAGE", (.35, .9, .6))]


def d_killfeed(S):
    cid = uid("kf")
    g = [f'<clipPath id="{cid}"><rect x="0" y="0" width="408" height="200"/></clipPath><g clip-path="url(#{cid})">']
    para = Track((0.0, 0.0)).linear(S + .2, S + 3.5, (-90.0, 0.0))
    g.append(f'<g>{para.transform("translate", CLK)}<text x="-10" y="150" font-size="104" font-weight="800" fill="none" '
             f'stroke="#1e293b" stroke-width="1.5">AGENTS</text></g>')
    scroll = Track((0.0, 0.0)).linear(S + .2, S + 3.5, (-250.0, 0.0))
    cards = []
    for i, (role, name, stats) in enumerate(AGENTS):
        x, t = 8 + i * 118, S + .25 + i * .07
        rise_y = Track((0.0, 36.0)).spring(t, (0.0, 0.0), "default")
        card = (f'<rect x="{x}" y="14" width="104" height="172" rx="10" fill="{NODE_FILL}" stroke="{DEEP}"/>'
                f'<path d="M{x + 52} 44l14 14-14 14-14-14z" fill="none" stroke="{CYAN}" stroke-width="1.5"/>'
                + txt(x + 52, 98, role, 9.5, DIM, 700, "middle", 'letter-spacing="1.2"')
                + txt(x + 52, 120, name, 15, WHITE, 800, "middle"))
        for j, s in enumerate(stats):
            card += (f'<rect x="{x + 14}" y="{138 + j * 14}" width="76" height="5" rx="2.5" fill="#1e293b"/>'
                     f'<rect x="{x + 14}" y="{138 + j * 14}" width="{76 * s:.1f}" height="5" rx="2.5" fill="{CYAN}" opacity="{.55 + .15 * j}"/>')
        cards.append(f'<g opacity="0">{visible(CLK, t)}<g>{rise_y.transform("translate", CLK)}{card}</g></g>')
    g.append(f'<g>{scroll.transform("translate", CLK)}{"".join(cards)}</g></g>')
    # head-damage falloff: Vandal holds 160, Phantom steps down with range
    def py(dmg):
        return 300 - (dmg - 115) * 1.6

    def px(m):
        return 40 + m * 7.2

    g.append(f'<line x1="40" y1="300" x2="400" y2="300" stroke="{LINE}"/>' + txt(0, 228, "head", 10, DIM) + txt(0, 240, "dmg", 10, DIM)
             + txt(400, 316, "50 m", 10, DIM, anchor="end") + txt(40, 316, "0 m", 10, DIM))
    vandal = f"M{px(0)} {py(160)}H{px(50)}"
    phantom = f"M{px(0)} {py(156)}H{px(15)}V{py(140)}H{px(30)}V{py(124)}H{px(50)}"
    g.append(draw(vandal, 364, CLK, S + 1.6, f'stroke="{WHITE}" stroke-width="2"', "heavy"))
    g.append(draw(phantom, 360 + 2 * 25.6 + 4, CLK, S + 1.85, f'stroke="{CYAN}" stroke-width="2"', "heavy"))
    g.append(chip(px(42), py(160) - 14, "vandal 160", S + 2.4, None, 10, WHITE, "#111827"))
    g.append(chip(px(40), py(124) - 14, "phantom 124", S + 2.55, None, 10))
    return "".join(g)


def d_arxchess(S):
    sq, oy = 32, 30
    defs = "".join(chess.svg.PIECES.values())
    g = [f'<defs>{defs}</defs>']
    for f in range(8):
        for r in range(8):
            light = (f + r) % 2 == 1
            g.append(f'<rect x="{f * sq}" y="{oy + (7 - r) * sq}" width="{sq}" height="{sq}" fill="{"#94a3b8" if light else "#475569"}"/>')
    moves = [("e2", "e4", .6), ("e7", "e5", 1.1), ("g1", "f3", 1.6), ("b8", "c6", 2.1), ("f1", "b5", 2.6)]

    def xy(sqn):
        return (ord(sqn[0]) - 97) * sq, oy + (7 - (int(sqn[1]) - 1)) * sq

    # last-move highlights
    for i, (a, b, t) in enumerate(moves):
        end = moves[i + 1][2] if i + 1 < len(moves) else None
        for s in (a, b):
            x, y = xy(s)
            g.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{CYAN}" opacity="0">'
                     f'{Track(0.0).snap(S + t, .38).snap(S + end, 0.0).animate("opacity", CLK) if end else Track(0.0).snap(S + t, .38).animate("opacity", CLK)}</rect>')
    board = chess.Board()
    moved = {a: (b, t) for a, b, t in moves}
    k = sq / 45
    for square, piece in board.piece_map().items():
        name = chess.square_name(square)
        x, y = xy(name)
        pid = f'{"white" if piece.color else "black"}-{chess.piece_name(piece.piece_type)}'
        use = f'<use href="#{pid}" xlink:href="#{pid}" transform="scale({k:.4f})"/>'
        if name in moved:
            to, t = moved[name]
            tx, ty = xy(to)
            tr = Track((float(x), float(y))).spring(S + t, (float(tx), float(ty)), "snappy")
            g.append(f'<g>{tr.transform("translate", CLK)}{use}</g>')
        else:
            g.append(f'<g transform="translate({x} {y})">{use}</g>')
    # eval bar (white share from the bottom)
    evals = [(.6, .53), (1.1, .51), (1.6, .54), (2.1, .52), (2.6, .56)]
    h = 8 * sq
    ht = Track(h * .5)
    yt = Track(oy + h * .5)
    for t, share in evals:
        ht.spring(S + t + .1, h * share, "default")
        yt.spring(S + t + .1, oy + h * (1 - share), "default")
    g.append(f'<rect x="264" y="{oy}" width="10" height="{h}" rx="3" fill="#111827"/>'
             f'<rect x="264" y="{oy + h / 2}" width="10" height="{h / 2}" rx="3" fill="{WHITE}">'
             f'{ht.animate("height", CLK)}{yt.animate("y", CLK)}</rect>')
    rows = [("1.", "e4", "e5"), ("2.", "Nf3", "Nc6"), ("3.", "Bb5", "")]
    for i, (n, w, b) in enumerate(rows):
        y = oy + 22 + i * 22
        g.append(rise(txt(290, y, n, 12, DIM), CLK, (288, y - 14, 20, 19), S + moves[i * 2][2], None, "snappy"))
        g.append(rise(txt(314, y, w, 12, WHITE, 700), CLK, (312, y - 14, 40, 19), S + moves[i * 2][2], None, "snappy"))
        if b:
            g.append(rise(txt(356, y, b, 12, WHITE, 700), CLK, (354, y - 14, 44, 19), S + moves[i * 2 + 1][2], None, "snappy"))
    g.append(rise(txt(290, oy + 104, "Ruy Lopez", 13, CYAN, 700), CLK, (288, oy + 89, 118, 20), S + 2.95, None, "default"))
    g.append(rise(txt(290, oy + 124, "stockfish +0.4", 11.5, DIM), CLK, (288, oy + 111, 118, 18), S + 3.05, None, "default"))
    return "".join(g)


SUBAGENTS = ["planning", "data_analyst", "decider", "predictive_model", "chartered"]


def d_personafi(S):
    import math
    cx, cy = 204, 140
    pos = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pos.append((cx + 158 * math.cos(a), cy + 112 * math.sin(a)))
    g, pk = [], []
    for i, (x, y) in enumerate(pos):
        g.append(line(cx, cy, round(x, 1), round(y, 1), S + .3 + i * .06, LINE, 1.5))
    g.append("{PACKETS}")
    g.append(pop(node(cx - 62, cy - 18, 124, 36, "master_agent", 12, WHITE), CLK, cx, cy, S + .2, None, .8, "default"))
    for i, ((x, y), name) in enumerate(zip(pos, SUBAGENTS)):
        w = len(name) * 7 + 22
        g.append(pop(node(round(x - w / 2, 1), round(y - 14, 1), w, 28, name, 11), CLK, x, y, S + .45 + i * .06))
    for k, (idx, t) in enumerate([(1, 1.0), (0, 1.75), (2, 2.4)]):
        x, y = pos[idx]
        p0, p1 = (float(cx), float(cy)), (round(x, 1), round(y, 1))
        pk.append(packet([p0, p1], [(S + t, S + t + .3)], S + t, S + t + .32))
        w = len(SUBAGENTS[idx]) * 7 + 22
        g.append(flash(round(x - w / 2, 1), round(y - 14, 1), w, 28, S + t + .3, .2))
        pk.append(packet([p1, p0], [(S + t + .38, S + t + .66)], S + t + .36, S + t + .7, WHITE))
    analysts = "bank · credit · epf · mf · net worth · stock"
    g.append(rise(txt(204, 300, analysts, 11.5, PALE, anchor="middle"), CLK, (0, 286, 408, 19), S + 1.4, None, "default"))
    g.append(rise(txt(204, 282, "data_analyst fans out to", 10.5, DIM, anchor="middle"), CLK, (0, 270, 408, 16), S + 1.32, None, "default"))
    return "".join(g).replace("{PACKETS}", "".join(pk))


def d_nutriquest(S):
    g = [f'<rect x="0" y="10" width="190" height="62" rx="10" fill="{NODE_FILL}" stroke="{DEEP}"/>',
         txt(14, 32, "meal log", 10.5, DIM),
         typed(f'style="font-size:13px;fill:{WHITE};font-weight:700"', "dal, rice, salad", CLK, 14, 56, S + .45, 7.8, cps=30, size=13),
         chip(64, 100, "gemini · parse", S + 1.05)]
    for i, (macro, stat) in enumerate([("protein 18g", "STR"), ("fiber 9g", "END"), ("vitamins A, C", "VIT")]):
        y = 142 + i * 22
        g.append(rise(txt(0, y, macro, 12, TEXT) + txt(118, y, "→", 12, DIM) + txt(140, y, stat, 12, CYAN, 700),
                      CLK, (0, y - 14, 190, 19), S + 1.25 + i * .1, None, "default"))
    g.append(pop(txt(95, 236, "+120 XP", 24, CYAN, 800, "middle"), CLK, 95, 228, S + 1.75, None, .5))
    # hero card
    g.append(f'<rect x="214" y="10" width="194" height="296" rx="12" fill="{NODE_FILL}" stroke="{DEEP}"/>'
             + txt(230, 38, "Warrior", 15, WHITE, 800))
    for lv, (a, b) in [(4, (S + .1, S + 2.5)), (5, (S + 2.5, None))]:
        g.append(rise(txt(392, 38, f"LVL {lv}", 13, CYAN, 700, "end"), CLK, (330, 24, 70, 19), a, b, "snappy"))
    g.append(txt(230, 62, "XP", 10.5, DIM))
    xp = Track(0.0).spring(S + .3, 100.0, "default").spring(S + 1.95, 160.0, "default").set(S + 2.5, 0.0).spring(S + 2.55, 24.0, "snappy")
    g.append(f'<rect x="254" y="54" width="140" height="8" rx="4" fill="#1e293b"/>'
             f'<rect x="254" y="54" width="0" height="8" rx="4" fill="{CYAN}">{xp.animate("width", CLK)}</rect>')
    g.append(chip(311, 90, "LEVEL UP", S + 2.5))
    base = [.52, .40, .46, .36, .44]
    gain = [.20, .12, .02, .03, .17]
    for i, stat in enumerate(["STR", "VIT", "AGI", "INT", "END"]):
        y = 128 + i * 34
        g.append(txt(230, y + 8, stat, 11.5, PALE, 700))
        tr = Track(0.0).spring(S + .35 + i * .05, 126 * base[i], "heavy").spring(S + 2.0 + i * .06, 126 * (base[i] + gain[i]), "heavy")
        g.append(f'<rect x="268" y="{y}" width="126" height="8" rx="4" fill="#1e293b"/>'
                 f'<rect x="268" y="{y}" width="0" height="8" rx="4" fill="{CYAN}">{tr.animate("width", CLK)}</rect>')
        if gain[i] > .1:
            g.append(rise(txt(394, y - 4, f"+{round(gain[i] * 50)}", 10.5, CYAN, 700, "end"), CLK, (360, y - 16, 36, 15),
                          S + 2.1 + i * .06, None, "snappy"))
    return "".join(g)


SHOTS = [
    ("01 · web infrastructure", "AXL", "URL shortener",
     "Redis cache-aside redirects. Click tracking runs after the response and flushes to Postgres in batches.",
     "next.js · supabase · redis", ("● LIVE", "#22c55e"), "axl.arxstudios.pro", d_axl),
    ("02 · security · web3", "ChronoVault", "encrypted, sharded file vault",
     "AES-256-GCM in the browser, shards pinned to IPFS, integrity proven by a Merkle root on Ethereum.",
     "react · ipfs · ethereum · facenet", ("● LIVE", "#22c55e"), "chronovault-psi.vercel.app", d_chronovault),
    ("03 · compilers", "ANX", "a compiled language",
     "Java-like syntax for DSA practice, with a tree-walking interpreter and an LLVM 21 native backend.",
     "rust · llvm 21", ("● BUILDING", "#f59e0b"), "arx-studios/arx-native-executable", d_anx),
    ("04 · compilers", "ArxCy", "transpiles to C",
     "A statically typed language for beginners: ANTLR4 grammar, a C++ code-gen visitor, standard C out.",
     "c++17 · antlr4 · cmake", ("● SHIPPED", CYAN), "cyborgwastaken/ArxCy", d_arxcy),
    ("05 · frontend", "Arx Killfeed", "a cinematic valorant codex",
     "Scroll-driven pages for agents, weapons, maps and ranks, generated statically from a data pipeline.",
     "next.js · gsap · lenis", ("● LIVE", "#22c55e"), "arx-killfeed.vercel.app", d_killfeed),
    ("06 · realtime", "ArxChess", "a full chess platform",
     "Stockfish AI, an analysis board, puzzles, an engine-vs-engine arena and real-time online rooms.",
     "next.js · stockfish wasm · websockets", ("● BUILDING", "#f59e0b"), "arx-studios/arxchess", d_arxchess),
    ("07 · multi-agent ai", "PersonaFi", "an AI financial assistant",
     "A master agent routes each question to five sub-agents, backed by a Fi Money MCP server.",
     "google adk · gemini · vertex ai", ("★ FINALIST", "#a78bfa"), "Google Agentic AI Day 2025", d_personafi),
    ("08 · ai · gamification", "NutriQuest", "nutrition, as an RPG",
     "Gemini reads your meal: protein becomes STR, fiber becomes END, and your hero levels up.",
     "react 19 · fastapi · gemini", ("★ FINALIST", "#a78bfa"), "AMD Slingshot Prompt-a-thon", d_nutriquest),
]


def build() -> str:
    out = [frame(W, H, "~/showreel — ▶ playing").replace(
        '<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"')]
    seg_gap, track_x, track_w = 6, 40, W - 80
    seg_w = (track_w - seg_gap * (N - 1)) / N

    for k, (eyebrow, title, tagline, detail, stack, (status, scol), where, diagram) in enumerate(SHOTS):
        S = k * SHOT
        x_out = S + 3.42
        # shot counter in the title bar
        out.append(f'<text x="{W - 24}" y="22" text-anchor="end" class="title" opacity="0">{k + 1:02d} / {N:02d}'
                   f'{visible(CLK, S, S + SHOT, snap=False)}</text>')
        # left column: masked rises, sequential in, lift out before the next shot lands
        rows = [(txt(40, 96, eyebrow, 12, DIM, 400, extra='letter-spacing="1"'), (36, 82, 380, 19)),
                (txt(40, 144, title, 36, WHITE, 800), (36, 110, 380, 46)),
                (txt(40, 174, tagline, 15, CYAN, 600), (36, 158, 380, 22))]
        for i, ln in enumerate(wrap(detail, 46)):
            rows.append((txt(40, 210 + i * 21, ln, 13, TEXT), (36, 196 + i * 21, 380, 19)))
        rows.append((txt(40, 300, "$ ", 12.5, DEEP, 700) + txt(56, 300, stack, 12.5, DIM), (36, 286, 380, 19)))
        rows.append((txt(40, 330, status, 12, scol, 800) + txt(40 + (len(status) + 2) * 7.4, 330, where, 12, DIM),
                     (36, 316, 380, 19)))
        for i, (svg, box) in enumerate(rows):
            out.append(rise(svg, CLK, box, S + .02 + i * .07, x_out + i * .025, "heavy"))

        # right column: diagram grows in, drifts (micro push), collapses out
        cx, cy = DX + 204, DY + 160
        sc = Track(0.9).spring(S + .1, 1.0, "default").linear(S + .1 + settle("default"), x_out, 1.03)
        sc.spring(x_out, 0.94, "snappy").set(S + 3.9, 0.9)
        out.append(f'<g opacity="0">{visible(CLK, S + .1, x_out + .12)}<g transform="translate({cx} {cy})"><g>'
                   f'{sc.transform("scale", CLK)}<g transform="translate({DX - cx} {DY - cy})">{diagram(S)}</g></g></g></g>')

        # scrubber segment k fills during its shot
        sx = track_x + k * (seg_w + seg_gap)
        fill = Track(0.0).linear(S, S + SHOT, seg_w)
        out.append(f'<rect x="{sx:.1f}" y="{H - 34}" width="{seg_w:.1f}" height="4" rx="2" fill="#1e293b"/>'
                   f'<rect x="{sx:.1f}" y="{H - 34}" width="0" height="4" rx="2" fill="{CYAN}">{fill.animate("width", CLK)}</rect>')

    out.append(f'<text x="{track_x}" y="{H - 44}" class="dim" font-size="11">▶ showreel</text>'
               f'<text x="{W - 40}" y="{H - 44}" class="dim" font-size="11" text-anchor="end">8 projects · loops</text>')
    out.append(overlay(W, H))
    return "\n".join(out)


if __name__ == "__main__":
    svg = build()
    (ROOT / "reel.svg").write_text(svg, encoding="utf-8")
    print(f"wrote reel.svg ({len(svg) / 1024:.0f} KB)")
