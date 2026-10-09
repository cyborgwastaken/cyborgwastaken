"""Community chess for the GitHub profile README: visitors play White, Stockfish plays Black.

A visitor clicks a move link in the README, which opens a pre-filled issue titled `chess|move|e2e4`
(or `chess|new`). The `chess.yml` workflow runs this script, which validates the move, lets Stockfish
reply, redraws the board, rewrites the README section between the CHESS markers and writes a comment
for the issue.

    python profile/chess/game.py issue    # reads TITLE / PLAYER from the environment (CI)
    python profile/chess/game.py render   # redraw board + README from state.json without moving
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import chess
import chess.engine
import chess.svg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
STATE = HERE / "state.json"
BOARD = HERE / "board.svg"
README = ROOT / "README.md"

REPO = "cyborgwastaken/cyborgwastaken"
SKILL_LEVEL = 4  # 0–20; low enough that a careful human can win
THINK_TIME = 0.25
START, END = "<!--CHESS:START-->", "<!--CHESS:END-->"

PIECE_NAMES = {chess.PAWN: "Pawn", chess.KNIGHT: "Knight", chess.BISHOP: "Bishop",
               chess.ROOK: "Rook", chess.QUEEN: "Queen", chess.KING: "King"}
PIECE_GLYPHS = {chess.PAWN: "♙", chess.KNIGHT: "♘", chess.BISHOP: "♗",
                chess.ROOK: "♖", chess.QUEEN: "♕", chess.KING: "♔"}


def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"game": 1, "fen": chess.STARTING_FEN, "moves": [], "record": {"visitors": 0, "stockfish": 0, "draws": 0},
            "players": {}}


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def new_game(state: dict) -> None:
    state["game"] += 1
    state["fen"] = chess.STARTING_FEN
    state["moves"] = []


def engine_reply(board: chess.Board) -> chess.Move:
    path = os.environ.get("STOCKFISH") or shutil.which("stockfish") or "/usr/games/stockfish"
    with chess.engine.SimpleEngine.popen_uci(path) as engine:
        engine.configure({"Skill Level": SKILL_LEVEL})
        return engine.play(board, chess.engine.Limit(time=THINK_TIME)).move


def finish(state: dict, board: chess.Board) -> str:
    """Record a finished game, start a new one, and describe the result."""
    outcome = board.outcome()
    if outcome.winner is chess.WHITE:
        state["record"]["visitors"] += 1
        text = "**Checkmate, the visitors win!** 🎉 Stockfish has been defeated."
    elif outcome.winner is chess.BLACK:
        state["record"]["stockfish"] += 1
        text = "**Checkmate, Stockfish wins.** 🤖 Better luck next game."
    else:
        state["record"]["draws"] += 1
        text = f"**Draw** ({outcome.termination.name.replace('_', ' ').lower()})."
    new_game(state)
    return text + f" A fresh board is up for game #{state['game']}."


def play(state: dict, title: str, player: str) -> str:
    m = re.fullmatch(r"chess\|(new|move\|([a-h][1-8][a-h][1-8][qrbn]?))", title.strip())
    if not m:
        return "🤔 I couldn't read that. Use the move links in the README, which create the issue for you."

    board = chess.Board(state["fen"])
    if m.group(1) == "new":
        if board.fullmove_number < 4:
            return "♟️ The current game has barely started, so I left it alone. Make a move instead!"
        new_game(state)
        return f"🔄 New game started (#{state['game']}). You're White, it's your move."

    move = chess.Move.from_uci(m.group(2))
    if move not in board.legal_moves:
        return (f"⛔ `{m.group(2)}` isn't legal in the current position. Someone probably moved first. "
                "Head back to the README for the updated board.")

    san = board.san(move)
    board.push(move)
    state["moves"].append({"by": player, "uci": move.uci(), "san": san})
    state["players"][player] = state["players"].get(player, 0) + 1
    reply = f"✅ @{player} played **{san}**."

    if board.is_game_over():
        state["fen"] = board.fen()
        return reply + " " + finish(state, board)

    answer = engine_reply(board)
    answer_san = board.san(answer)
    board.push(answer)
    state["moves"].append({"by": "stockfish", "uci": answer.uci(), "san": answer_san})
    reply += f" Stockfish answered **{answer_san}**."
    state["fen"] = board.fen()

    if board.is_game_over():
        reply += " " + finish(state, board)
    elif board.is_check():
        reply += " You're in check!"
    return reply


def issue_link(title: str) -> str:
    body = "Just press **Submit new issue**. The game updates automatically within a minute or so."
    return f"https://github.com/{REPO}/issues/new?title={quote(title, safe='')}&body={quote(body)}"


def render(state: dict) -> None:
    board = chess.Board(state["fen"])
    last = chess.Move.from_uci(state["moves"][-1]["uci"]) if state["moves"] else None
    svg = chess.svg.board(
        board,
        lastmove=last,
        check=board.king(board.turn) if board.is_check() else None,
        size=440,
        coordinates=True,
        colors={
            "square light": "#cbd5e1", "square dark": "#3b5268",
            "square light lastmove": "#67e8f9", "square dark lastmove": "#0e7490",
            "margin": "#0a0e14", "coord": "#64748b", "inner border": "#1e293b", "outer border": "#1e293b",
        },
    )
    BOARD.write_text(svg, encoding="utf-8")

    # legal moves grouped by the piece that makes them
    groups: dict[chess.Square, list[chess.Move]] = {}
    for mv in board.legal_moves:
        groups.setdefault(mv.from_square, []).append(mv)
    order = sorted(groups, key=lambda sq: (board.piece_type_at(sq), sq))
    rows = []
    for sq in order:
        piece = board.piece_type_at(sq)
        links = " · ".join(
            f"[`{board.san(mv)}`]({issue_link('chess|move|' + mv.uci())})"
            for mv in sorted(groups[sq], key=lambda mv: board.san(mv))
        )
        rows.append(f"| {PIECE_GLYPHS[piece]} {PIECE_NAMES[piece]} on `{chess.square_name(sq)}` | {links} |")

    recent = [m for m in state["moves"] if m["by"] != "stockfish"][-5:][::-1]
    recent_md = " ".join(f"[@{m['by']}](https://github.com/{m['by']}) `{m['san']}`" for m in recent) or "_nobody yet, be the first_"
    top = sorted(state["players"].items(), key=lambda kv: -kv[1])[:5]
    top_md = " · ".join(f"[@{p}](https://github.com/{p}) ({n})" for p, n in top) or "_empty, claim the top spot_"
    rec = state["record"]
    last_line = ""
    if len(state["moves"]) >= 2:
        h, s = state["moves"][-2], state["moves"][-1]
        last_line = f" Last turn: [@{h['by']}](https://github.com/{h['by']}) played `{h['san']}`, Stockfish replied `{s['san']}`."
    turn_text = "check! " if board.is_check() else ""
    version = f"{state['game']}-{len(state['moves'])}"

    section = f"""{START}
<p align="center"><img src="profile/chess/board.svg?v={version}" width="440" alt="current chess board"></p>

<p align="center"><b>Game #{state['game']} · move {board.fullmove_number} · you're White, {turn_text}your move.</b><br />
<sub>Stockfish (skill {SKILL_LEVEL}/20) plays Black and replies instantly.{last_line}</sub></p>

<details>
<summary><b>♟️ Make a move</b>: {board.legal_moves.count()} legal moves. Click one, then hit <i>Submit new issue</i>.</summary>
<br />

| Piece | Moves |
|---|---|
{chr(10).join(rows)}

<sub>Game stuck or lost? [Start a new game]({issue_link('chess|new')}).</sub>
</details>

| 🏆 Visitors vs Stockfish | 🕹️ Latest moves | 👑 Most moves played |
|:-:|:-:|:-:|
| **{rec['visitors']}** wins · **{rec['stockfish']}** losses · **{rec['draws']}** draws | {recent_md} | {top_md} |
{END}"""

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        sys.exit(f"README is missing the {START} / {END} markers")
    README.write_text(pattern.sub(lambda _: section, readme), encoding="utf-8")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    state = load()
    if cmd == "issue":
        comment = play(state, os.environ["TITLE"], os.environ["PLAYER"])
        save(state)
        Path(os.environ.get("COMMENT_FILE", HERE / ".comment.md")).write_text(
            comment + f"\n\n[Back to the board ↗](https://github.com/{REPO}#play-chess-against-my-readme)\n",
            encoding="utf-8",
        )
        print(comment)
    elif cmd == "render":
        save(state)
    else:
        sys.exit(f"unknown command {cmd}")
    render(state)


if __name__ == "__main__":
    main()
