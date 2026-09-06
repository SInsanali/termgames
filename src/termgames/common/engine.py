"""Shared scaffolding for every game screen.

Every game in this repo follows the same control scheme:

    WASD / arrows   steer
    space           pause / resume
    r               restart (while paused or on game over)
    esc             exit to the launcher

Subclasses implement the grid logic (``reset``, ``tick``, ``build_frame``)
and get bindings, the pause/game-over state machine, a resizable timer loop,
themed borders, and high-score persistence for free.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static

from . import leaderboard, scores
from .name_entry import NameEntryScreen
from .theme import get_theme

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


class BaseGameScreen(ModalScreen):
    """Base class for a single-player (or shared-keyboard) game screen."""

    GAME_ID = "base"          # override: used as the high-score file key
    GAME_TITLE = "GAME"       # override: shown in the header
    BASE_INTERVAL = 0.15      # seconds between ticks
    MIN_INTERVAL = 0.05

    # Fallback board size, used only if the terminal size isn't available yet.
    # Normally overridden per-instance by _autosize() at game start, so the
    # board fills most of the actual terminal rather than a fixed constant —
    # fixed for the length of one game (see the class docstring), not this
    # hardcoded number.
    BOARD_W = 30
    BOARD_H = 18
    CELL_W = 2                # terminal columns per cell
    CELL_H = 1                # terminal rows per cell — raise this (with a
                               # matching CELL_W bump) for chunkier, more
                               # visible pieces on a game with few of them
                               # (e.g. Snake's short body), rather than more
                               # tiny cells filling the same space.

    # Fixed rows around the board, used by both compose() and _autosize():
    # title line + SCORE/HIGH line, top+bottom border, one status line.
    HEADER_ROWS = 2
    BORDER_ROWS = 2
    FOOTER_ROWS = 1

    # Bounds for _autosize() — keep the board playable on a tiny terminal and
    # sane (not absurdly huge) on a giant one. In *cells*, not terminal
    # rows/cols, so a game with bigger CELL_W/CELL_H should tighten these.
    MIN_BOARD_W = 20
    MAX_BOARD_W = 90
    MIN_BOARD_H = 14
    MAX_BOARD_H = 44
    # Extra breathing room beyond the fixed header/border/footer rows.
    AUTOSIZE_MARGIN_W = 4
    AUTOSIZE_MARGIN_H = 2

    BINDINGS = [
        Binding("up", "steer('up')", show=False),
        Binding("w", "steer('up')", show=False),
        Binding("down", "steer('down')", show=False),
        Binding("s", "steer('down')", show=False),
        Binding("left", "steer('left')", show=False),
        Binding("a", "steer('left')", show=False),
        Binding("right", "steer('right')", show=False),
        Binding("d", "steer('right')", show=False),
        Binding("space", "toggle_pause", show=False),
        Binding("r", "restart", show=False),
        # Both keys leave the game and return to the launcher. A game screen
        # has no text entry, so "q" is free to mirror escape here — the same
        # pair quits the launcher itself, so one habit works everywhere.
        Binding("escape", "dismiss", show=False),
        Binding("q", "dismiss", show=False),
    ]

    # DEFAULT_CSS (not CSS) so this cascades to every subclass automatically —
    # Textual only auto-applies a plain `CSS` block to the exact class that
    # defines it, not to subclasses that don't redeclare their own.
    DEFAULT_CSS = """
    BaseGameScreen {
        align: center middle;
        background: $background;
    }
    #game {
        content-align: center middle;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._timer = None
        self._high = scores.load(self.GAME_ID)
        self._score = 0
        self._state = "playing"

    # ── lifecycle ──────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        self._autosize()
        self.reset()
        g = Static(self._frame(), id="game")
        g.styles.width = self.BOARD_W * self.CELL_W + 2
        g.styles.height = (
            self.BOARD_H * self.CELL_H + self.HEADER_ROWS + self.BORDER_ROWS + self.FOOTER_ROWS
        )
        yield g

    def _autosize(self) -> None:
        """Size the board to fill most of the terminal, once, at game start
        (fixed for the rest of the game — see the class docstring for why
        not a board that grows mid-game)."""
        screen_w, screen_h = self.app.size
        if not screen_w or not screen_h:
            return
        chrome_h = self.HEADER_ROWS + self.BORDER_ROWS + self.FOOTER_ROWS
        avail_w = max(1, screen_w - self.AUTOSIZE_MARGIN_W)
        avail_h = max(1, screen_h - chrome_h - self.AUTOSIZE_MARGIN_H)
        self.BOARD_W = max(self.MIN_BOARD_W, min(self.MAX_BOARD_W, avail_w // self.CELL_W))
        self.BOARD_H = max(self.MIN_BOARD_H, min(self.MAX_BOARD_H, avail_h // self.CELL_H))

    def on_mount(self) -> None:
        self._timer = self.set_interval(self.BASE_INTERVAL, self._on_tick)

    # ── hooks subclasses implement ────────────────────────────────────

    def reset(self) -> None:
        """Reset board/score/state for a new game. Must set self._score = 0."""
        raise NotImplementedError

    def tick(self) -> None:
        """Advance the game one step. Call self.game_over() on loss,
        and bump self._score / call self.respeed() on scoring events."""
        raise NotImplementedError

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        """Return the board rows (Rich markup), excluding header/footer/border."""
        raise NotImplementedError

    def steer(self, direction: str) -> None:
        """Handle a directional input. Default: no-op (override for movement)."""

    def status_line(self) -> str | None:
        """Optional extra line shown under the board while playing."""
        return None

    # ── game loop ──────────────────────────────────────────────────────

    def _on_tick(self) -> None:
        if self._state != "playing":
            return
        self.tick()
        self._redraw()

    def respeed(self, per_point: float = 0.004) -> None:
        """Speed the tick loop up as the score grows. Call after scoring."""
        interval = max(self.MIN_INTERVAL, self.BASE_INTERVAL - self._score * per_point)
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(interval, self._on_tick)

    def game_over(self) -> None:
        self._state = "over"
        if self._timer is not None:
            self._timer.pause()
        if self._score > self._high:
            self._high = self._score
            scores.save(self.GAME_ID, self._high)
        self._redraw()

        if leaderboard.qualifies(self.GAME_ID, self._score):
            rank = leaderboard.rank_for(self.GAME_ID, self._score)

            def handle_name(name: str | None) -> None:
                if name:
                    leaderboard.add(self.GAME_ID, name, self._score)

            self.app.push_screen(NameEntryScreen(self._score, rank), handle_name)

    # ── input ──────────────────────────────────────────────────────────

    def action_steer(self, direction: str) -> None:
        if self._state != "playing":
            return
        self.steer(direction)

    def action_toggle_pause(self) -> None:
        if self._state == "playing":
            self._state = "paused"
            if self._timer is not None:
                self._timer.pause()
        elif self._state == "paused":
            self._state = "playing"
            if self._timer is not None:
                self._timer.resume()
        self._redraw()

    def action_restart(self) -> None:
        if self._state not in ("paused", "over"):
            return
        self.reset()
        self._state = "playing"
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(self.BASE_INTERVAL, self._on_tick)
        self._redraw()

    # ── rendering ──────────────────────────────────────────────────────

    def _redraw(self) -> None:
        self.query_one("#game", Static).update(self._frame())

    def _center(self, plain: str, markup: str, width: int) -> str:
        pad = max(0, (width - len(plain)) // 2)
        return " " * pad + markup

    def _frame(self) -> str:
        theme = get_theme(self.app)
        accent, secondary = theme["accent"], theme["secondary"]
        width = self.BOARD_W * self.CELL_W + 2

        title_spaced = " ".join(self.GAME_TITLE)
        rows = [self._center(title_spaced, f"[bold {accent}]{title_spaced}[/]", width)]

        score_plain = f" SCORE {self._score} "
        high_plain = f" HIGH {self._high} "
        rows.append(self._center(
            f"{score_plain}  {high_plain}",
            f"[bold black on {accent}]{score_plain}[/]  [bold black on {secondary}]{high_plain}[/]",
            width,
        ))

        rows.append(f"[{accent}]╔{'═' * (self.BOARD_W * self.CELL_W)}╗[/]")
        for line in self.build_frame(theme):
            for _ in range(self.CELL_H):
                rows.append(f"[{accent}]║[/]{line}[{accent}]║[/]")
        rows.append(f"[{accent}]╚{'═' * (self.BOARD_W * self.CELL_W)}╝[/]")

        if self._state == "paused":
            rows.append(self._center(
                "PAUSED  —  space resume  r restart  esc exit",
                f"[bold {accent}]PAUSED[/]  [dim]—  space resume  r restart  esc exit[/]",
                width,
            ))
        elif self._state == "over":
            rows.append(self._center(
                f"GAME OVER  —  score {self._score}  —  r restart  esc exit",
                f"[bold {secondary}]GAME OVER[/]  [dim]— score {self._score} —  r restart  esc exit[/]",
                width,
            ))
        else:
            extra = self.status_line()
            text = extra or "wasd / arrows  space pause  esc exit"
            rows.append(self._center(text, f"[dim]{text}[/]", width))

        return "\n".join(rows)
