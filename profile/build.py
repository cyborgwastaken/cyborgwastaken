"""Builds every terminal panel used by the profile README (except the hero and telemetry, which have
their own builders). Re-run after editing any content below:

    python profile/build.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

from motion import Clock, pop
from term import (CHAR_W, CYAN, DEEP, DIM, PAD_X, TEXT, Panel, frame, overlay, reveal, typed, wrap)

OUT = Path(__file__).resolve().parent / "panels"
OUT.mkdir(exist_ok=True)


def write(name: str, svg: str) -> None:
    (OUT / name).write_text(svg, encoding="utf-8")
    print("wrote", name)


# ── about + career ─────────────────────────────────────────────────────────────
p = Panel("ayushman@arx-studios: ~ — zsh")
p.cmd("cat about.txt")
for line in [
    "I keep production boring so the product can be exciting.",
    "By day I build observability and reliability tooling for a live cybersecurity GRC platform",
    "at Cyberpal.ai. After hours I run Arx Studios, where I write compilers, ship web products",
    "and build games.",
]:
    p.add((line, ""))
p.blank()
p.cmd("journalctl -u career --reverse", "# most recent first")
career = [
    ("Feb 2026 → now", "cyberpal.ai", "Software Development Intern · Technology Crest Corporation", [
        "observability console streaming live stdout/stderr over WebSockets",
        "Prometheus metrics + Pino logs; alerts on heap, event-loop lag, error rate, p99",
        "distributed tracing with correlation IDs, automatic secret redaction in logs",
    ]),
    ("May–Jun 2025", "drdo-pxe", "R&D Intern · Defence Research & Development Organisation", [
        "built and deployed DRAD-MS and BLADEngine in a secure, access-controlled environment",
        "automated provisioning; killed recurring errors in the trajectory-tracking pipeline",
    ]),
    ("May–Jun 2024", "vit-serb", "Project Assistant · DST-SERB CRG research project", [
        "PyMOL/OpenGL molecular visualisation for Gaussian, GAMESS, NWChem and MOPAC",
    ]),
]
for when, unit, role, bullets in career:
    p.add((f"{when:<16}", "dim"), (f"{unit:<13}", "cy"), (role, "b"))
    for b in bullets:
        p.add((" " * 16, ""), ("› ", "deep"), (b, ""))
p.blank()
p.cmd("cat education.txt")
p.add(("2023–2027       ", "dim"), ("B.Tech CS&E", "b"), (" · VIT Bhopal · ", ""), ("CGPA 8.80", "ok"))
p.add(("2024–2028       ", "dim"), ("BS Data Science & Applications", "b"), (" · IIT Madras (online)", ""))
p.step = 0.07
write("about.svg", p.render())


# ── section dividers: a single typed prompt in a slim bar ─────────────────────
def divider(name: str, command: str, comment: str) -> None:
    w, h = 880, 50
    out = [frame(w, h, command, chrome=False)]
    out.append(f'<text x="{PAD_X - 14}" y="30" class="prompt" opacity="0">${reveal(0.15)}</text>')
    end = typed(out, command, PAD_X + 2, 30, 0.2, "d")
    out.append(f'<text x="{PAD_X + 2 + (len(command) + 3) * CHAR_W:.1f}" y="30" class="dim" opacity="0">'
               f'{escape(comment)}{reveal(end)}</text>')
    out.append(overlay(w, h, top=1))
    write(name, "\n".join(out))


divider("div-web.svg", "cd ~/deployments && ls", "# web, backend & infrastructure")
divider("div-lang.svg", "cd ~/compilers && ls", "# languages, compilers & native")
divider("div-ai.svg", "cd ~/ai && ls", "# agents, reinforcement learning, neuroevolution")
divider("div-games.svg", "cd ~/games && ls", "# unity, hdrp, game jams")


# ── project cards ──────────────────────────────────────────────────────────────
STATUS = {
    "live": ("● LIVE", "ok pulse"),
    "shipped": ("● SHIPPED", "cy"),
    "dev": ("● BUILDING", "warn pulse"),
    "award": ("★ FINALIST", "vi"),
}
CARD_W, DESC_CHARS = 432, 48

projects = [
    # file, path, status, where, name, tagline, description, stack
    ("axl", "~/arx-studios/axl", "live", "axl.arxstudios.pro", "AXL", "URL shortener",
     "Redis cache-aside redirects, click tracking that runs after the response, batched flushes to Postgres, rate limiting.",
     "next.js · supabase · redis"),
    ("chronovault", "~/chronovault", "live", "chronovault-psi.vercel.app", "ChronoVault", "encrypted file vault",
     "AES-256-GCM in the browser, shards on IPFS, Merkle roots on Ethereum. Time, geo and face-biometric unlock gates.",
     "react · ipfs · ethereum · facenet"),
    ("killfeed", "~/arx-studios/killfeed", "live", "arx-killfeed.vercel.app", "Arx Killfeed", "valorant codex",
     "A cinematic, scroll-driven encyclopedia of agents, weapons, maps and ranks, generated from a local data pipeline.",
     "next.js · gsap · lenis"),
    ("macnook", "~/arx-studios/macnook", "dev", "macnook.vercel.app", "MacNook", "quick look for folders",
     "Press Space on a folder in Finder and actually see what is inside it. A native Quick Look extension.",
     "swift · swiftui · next.js"),
    ("arxchess", "~/arx-studios/arxchess", "dev", "github", "ArxChess", "chess platform",
     "Stockfish AI, analysis board, puzzles, an engine-vs-engine arena and real-time online rooms.",
     "next.js · stockfish wasm · websockets"),
    ("arxstream", "~/arxstream", "shipped", "github", "arxstream", "two-person watch party",
     "Synced video playback, chat and a peer-to-peer webcam, deployable as a single Node service.",
     "node.js · websockets · webrtc"),
    ("anx", "~/arx-studios/anx", "dev", "github", "ANX", "a compiled language",
     "Built for DSA practice: a tree-walking interpreter and an LLVM native backend, 20 benchmarks green on both.",
     "rust · llvm 21"),
    ("arxcy", "~/arxcy", "shipped", "github", "ArxCy", "a language for beginners",
     "A small, statically typed, C-like language with an ANTLR4 grammar, transpiled to standard C.",
     "c++17 · antlr4"),
    ("personafi", "~/personafi", "award", "Google Agentic AI Day 2025", "PersonaFi", "multi-agent finance assistant",
     "A master agent routing to specialist sub-agents over a mock Fi Money MCP server. Finale, Bengaluru.",
     "google adk · gemini · vertex ai · go"),
    ("nutriquest", "~/nutriquest", "award", "AMD Slingshot Prompt-a-thon", "NutriQuest", "nutrition, as an RPG",
     "Meals become XP, stats and buffs for a hero, with Gemini parsing meals and playing the in-game Oracle.",
     "react 19 · fastapi · gemini"),
    ("artificiallife", "~/artificiallife", "shipped", "github", "ArtificialLife", "neuroevolution sandbox",
     "Creatures with 8-6-3 neural brains learn to forage through selection and mutation. No scripted behaviour.",
     "unity · c#"),
    ("snake-ai", "~/cy-snake-ai", "shipped", "github", "Cy-Snake-AI", "reinforcement learning",
     "A Deep Q-Learning agent that teaches itself Snake, with live training plots.",
     "pytorch · pygame"),
    ("nexion", "~/nexion", "dev", "final-year capstone", "NEXION", "cyberpunk puzzle-adventure",
     "Story-driven puzzles built around a human-vs-CPU dual-mode mechanic, with terminal and keypad puzzles.",
     "unity 6 · hdrp"),
    ("doofus", "~/doofus-adventure", "live", "play.unity.com", "Doofus Adventure", "3D platform hopper",
     "Built for the Hitwicket game developer challenge, with JSON-driven tuning. Playable in the browser.",
     "unity 6 · c#"),
]

desc_rows = max(len(wrap(d, DESC_CHARS)) for *_, d, _ in projects)
for file, path, status, where, name, tagline, desc, stack in projects:
    c = Panel(path, width=CARD_W, step=0.09, pad_bottom=20)
    label, cls = STATUS[status]
    c.add((label, cls), ("  " + where, "dim"))
    c.add((name, "big"), (f"  {tagline}", "cy"))
    lines = wrap(desc, DESC_CHARS)
    for line in lines:
        c.add((line, ""))
    for _ in range(desc_rows - len(lines)):
        c.blank()
    c.add(("$ ", "deep"), (stack, "dim"))
    write(f"card-{file}.svg", c.render())


# ── stack: tags drawn as chips ─────────────────────────────────────────────────
stack = [
    ("languages", ["java", "python", "go", "rust", "c#", "c++", "swift", "typescript"]),
    ("backend", ["node.js", "express", "socket.io", "fastapi", "next.js", "react"]),
    ("data", ["postgresql", "supabase", "redis", "sqlite"]),
    ("platform", ["prometheus", "pino", "docker", "kubernetes", "aws", "gcp", "linux"]),
    ("gamedev", ["unity", "unreal engine", "hdrp", "urp"]),
]
s = Panel("ayushman@arx-studios: ~ — zsh")
s.cmd("stack --list --group")
CHIP_CLOCK = Clock(6.0, loop=False)
chips, t0 = [], 0.25 + len("stack --list --group") / 40 + 0.1
for gi, (group, tags) in enumerate(stack):
    s.add((f"{group:<12}", "dim"))
    y = 36 + 34 + (gi + 1) * 22
    x = PAD_X + 12 * CHAR_W
    t = t0 + gi * s.step + 0.08  # tags follow their group label's rise
    for tag in tags:
        w = len(tag) * CHAR_W + 18
        chip_svg = (f'<rect x="{x:.1f}" y="{y - 15}" width="{w:.1f}" height="21" rx="5" fill="#0f1a24" stroke="{DEEP}"/>'
                    f'<text x="{x + 9:.1f}" y="{y}" class="cy">{escape(tag)}</text>')
        chips.append(pop(chip_svg, CHIP_CLOCK, x + w / 2, y - 4.5, t, None, .75))  # grow out, snappy spring
        x += w + 8
        t += 0.04
s.pad_bottom = 26
write("stack.svg", s.render(extra="\n".join(chips)))


# ── on-call / contact ──────────────────────────────────────────────────────────
o = Panel("ayushman@arx-studios: ~ — zsh", step=0.08)
o.cmd("cat ~/.oncall.yaml")
o.add(("on_call", "cy"), (": ", "dim"), ("ayushman", "b"))
o.add(("timezone", "cy"), (": ", "dim"), ("Asia/Kolkata", ""), ("  # IST, UTC+5:30", "dim"))
o.add(("escalation", "cy"), (":", "dim"))
for sev, target, note in [
    ("sev3", "open an issue on any repo", "# I read them"),
    ("sev2", "linkedin.com/in/ayuxcyb", "# roles, internships, collabs"),
    ("sev1", "ayushmandas.dudul@gmail.com", "# important? I'll reply"),
    ("sev0", "a game idea or a gnarly backend problem", "# page immediately"),
]:
    o.add(("  - ", "dim"), (sev, "warn" if sev == "sev0" else "vi"), (": ", "dim"), (f"{target:<42}", ""), (note, "dim"))
o.add(("open_to", "cy"), (": ", "dim"), ("[", "dim"), ("backend, platform / SRE, observability, game dev", "ok"), ("]", "dim"))
write("oncall.svg", o.render())


# ── link buttons ───────────────────────────────────────────────────────────────
buttons = [("site", "ayuxcyb.fun"), ("linkedin", "linkedin"), ("email", "email"),
           ("arx", "arx-studios"), ("instagram", "instagram")]
for i, (file, label) in enumerate(buttons):
    text = f"↗ {label}"
    w, h = int(len(text) * CHAR_W + 40), 40
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="{label}"><style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;'
           f'font-size:13px;fill:{CYAN};white-space:pre}}</style>'
           f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="9" fill="#0a0e14" stroke="{DEEP}"/>'
           f'<text x="20" y="25">{escape(text)}</text></svg>')
    write(f"btn-{file}.svg", svg)


# ── footer ─────────────────────────────────────────────────────────────────────
f = Panel("ayushman@arx-studios: ~ — zsh", pad_bottom=24)
f.cmd("exit")
f.add(("logout", "dim"))
f.add(("Connection to ayuxcyb.fun closed. ", ""), ("Thanks for stopping by.", "cy"))
svg = f.render()
y = 36 + 34 + 2 * 22
cursor_x = PAD_X + len("Connection to ayuxcyb.fun closed. Thanks for stopping by.") * CHAR_W + 6
svg = svg.replace("</svg>", f'<rect x="{cursor_x:.1f}" y="{y - 12}" width="8" height="15" fill="{CYAN}" opacity="0">'
                            f'<animate attributeName="opacity" values="1;0" dur="1.05s" begin="1.2s" '
                            f'repeatCount="indefinite" calcMode="discrete"/></rect></svg>')
write("footer.svg", svg)
