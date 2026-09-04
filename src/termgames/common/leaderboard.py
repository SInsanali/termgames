"""Per-game top-3 leaderboard: named scores, persisted to ~/.termgames/."""

import json
from pathlib import Path

LEADERBOARD_DIR = Path.home() / ".termgames" / "leaderboard"
TOP_N = 3


def load(game_id: str) -> list[dict]:
    try:
        data = json.loads((LEADERBOARD_DIR / f"{game_id}.json").read_text())
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    board = [e for e in data if isinstance(e, dict) and "name" in e and "score" in e]
    return board[:TOP_N]


def qualifies(game_id: str, score: int) -> bool:
    if score <= 0:
        return False
    board = load(game_id)
    if len(board) < TOP_N:
        return True
    return score > board[-1]["score"]


def rank_for(game_id: str, score: int) -> int:
    board = load(game_id)
    rank = 1 + sum(1 for e in board if e["score"] >= score)
    return min(rank, TOP_N)


def add(game_id: str, name: str, score: int) -> list[dict]:
    board = load(game_id)
    board.append({"name": name[:12] or "???", "score": score})
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:TOP_N]
    try:
        LEADERBOARD_DIR.mkdir(parents=True, exist_ok=True)
        (LEADERBOARD_DIR / f"{game_id}.json").write_text(json.dumps(board))
    except OSError:
        pass
    return board
