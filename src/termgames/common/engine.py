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
    CELL_W = 2                # terminal columns per cell, keeps cells ~square

    # Bounds for _autosize() — keep the board playable on a tiny terminal and
    # sane (not absurdly huge) on a giant one.
    MIN_BOARD_W = 20
    MAX_BOARD_W = 90
    MIN_BOARD_H = 14
    MAX_BOARD_H = 44
    # Reserved rows/cols around the board: header line + top/bottom border +
    # status line (4, fixed — see compose()) plus a little breathing room.
    AUTOSIZE_MARGIN_W = 4
    AUTOSIZE_MARGIN_H = 6

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
        Binding("escape", "dismiss", show=False),
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
        g.styles.height = self.BOARD_H + 4
        yield g

    def _autosize(self) -> None:
        """Size the board to fill most of the terminal, once, at game start
        (fixed for the rest of the game — see the class docstring for why
        not a board that grows mid-game)."""
        screen_w, screen_h = self.app.size
        if not screen_w or not screen_h:
            return
        avail_w = max(1, screen_w - self.AUTOSIZE_MARGIN_W)
        avail_h = max(1, screen_h - self.AUTOSIZE_MARGIN_H)
        self.BOARD_W = max(self.MIN_BOARD_W, min(self.MAX_BOARD_W, avail_w // self.CELL_W))
        self.BOARD_H = max(self.MIN_BOARD_H, min(self.MAX_BOARD_H, avail_h))

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

        rows = [self._center(
            f"{self.GAME_TITLE}    SCORE {self._score}    HIGH {self._high}",
            f"[bold {accent}]{self.GAME_TITLE}[/]    "
            f"[bold {accent}]SCORE[/] {self._score}    [bold {accent}]HIGH[/] {self._high}",
            width,
        )]
        rows.append(f"[{accent}]╔{'═' * (self.BOARD_W * self.CELL_W)}╗[/]")
        for line in self.build_frame(theme):
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
