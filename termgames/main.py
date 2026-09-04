"""termgames — a small collection of terminal games sharing one control
scheme: wasd/arrows to steer, space to pause, r to restart, esc to exit.

Run with:  python -m termgames
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.widgets import Footer, Header, ListItem, ListView, Label

from .breakout import BreakoutScreen
from .common.theme import THEMES
from .pong import PongScreen
from .tetris import TetrisScreen
from .tron import TronScreen
from .twenty48 import TwentyFortyEightScreen

GAMES = [
    ("Tetris", TetrisScreen, "wasd/arrows move+rotate, s soft-drop"),
    ("2048", TwentyFortyEightScreen, "wasd/arrows slide tiles"),
    ("Breakout", BreakoutScreen, "a/d or left/right move paddle"),
    ("Pong", PongScreen, "w/s or up/down move paddle, vs CPU"),
    ("Tron", TronScreen, "P1 wasd, P2 arrows, shared board"),
]


class Menu(ListView):
    pass


class TermGamesApp(App):
    TITLE = "termgames"
    CSS = """
    Screen {
        align: center middle;
    }
    #wrap {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
    }
    #subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("t", "cycle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    _active_theme = "viper"

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="wrap"):
                yield Label("Pick a game — enter to play, esc to return here.", id="subtitle")
                yield Menu(*(ListItem(Label(f"{name}  [dim]— {hint}[/]")) for name, _, hint in GAMES))
        yield Footer()

    def action_cycle_theme(self) -> None:
        ids = list(THEMES)
        self._active_theme = ids[(ids.index(self._active_theme) + 1) % len(ids)]
        self.refresh()

    def on_list_view_selected(self, event: Menu.Selected) -> None:
        index = event.list_view.index or 0
        _, screen_cls, _ = GAMES[index]
        self.push_screen(screen_cls())


def main() -> None:
    TermGamesApp().run()


if __name__ == "__main__":
    main()
