"""High-score persistence, one small text file per game under ~/.termgames/."""

from pathlib import Path

SCORES_DIR = Path.home() / ".termgames" / "scores"


def load(game_id: str) -> int:
    try:
        return int((SCORES_DIR / f"{game_id}.txt").read_text().strip())
    except (OSError, ValueError):
        return 0


def save(game_id: str, value: int) -> None:
    try:
        SCORES_DIR.mkdir(parents=True, exist_ok=True)
        (SCORES_DIR / f"{game_id}.txt").write_text(str(value))
    except OSError:
        pass
