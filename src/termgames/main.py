"""termgames — a small collection of terminal games sharing one control
scheme: wasd/arrows to steer, space to pause, r to restart, esc to exit.

Run with:  python -m termgames
"""

from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, ListItem, ListView, Static

from .breakout import BreakoutScreen
from .common.previews import PREVIEWS
from .common.theme import THEMES, get_theme
from .pong import PongScreen
from .tetris import TetrisScreen
from .tron import TronScreen
from .twenty48 import TwentyFortyEightScreen

GAMES = [
    ("tetris", "Tetris", TetrisScreen),
    ("2048", "2048", TwentyFortyEightScreen),
    ("breakout", "Breakout", BreakoutScreen),
    ("pong", "Pong", PongScreen),
    ("tron", "Tron", TronScreen),
]


class TermGamesApp(App):
    TITLE = "termgames"

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }

    #header {
        dock: top;
        height: auto;
        width: 100%;
        padding: 1 0 0 0;
    }


    #banner {
        text-align: center;
        text-style: bold;
    }

    #tagline {
        text-align: center;
        color: $text-muted;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
        margin: 1 2;
    }

    #games-panel {
        border: heavy $success;
        background: $surface;
        padding: 0 1;
        width: 1fr;
        border-title-color: $success;
        border-title-style: bold;
    }

    #preview-panel {
        border: heavy $accent;
        background: $surface;
        padding: 0 1 1 1;
        width: 2fr;
        border-title-color: $accent;
        border-title-style: bold;
    }

    #game-list {
        height: 1fr;
        background: transparent;
        scrollbar-color: $success;
    }

    ListView > ListItem {
        padding: 0 1;
        color: #888888;
        background: transparent;
    }

    ListView > ListItem:hover {
        background: $surface-lighten-1;
    }

    #game-list > ListItem.--highlight {
        background: $success-darken-3;
        color: $text;
    }

    #preview-art {
        height: auto;
        padding: 1 2;
        margin-bottom: 1;
    }

    #preview-tagline {
        text-style: italic;
        margin-bottom: 1;
    }

    #preview-controls-title {
        text-style: bold;
        color: $accent;
    }

    #status-bar {
        dock: bottom;
        height: 3;
        padding: 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("t", "cycle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    _active_theme = "viper"

    def compose(self) -> ComposeResult:
        with Vertical(id="header"):
            yield Static(self._banner_text(), id="banner")
            yield Static(
                "wasd / arrows steer   ·   space pause   ·   r restart   ·   esc exit",
                id="tagline",
            )
        with Horizontal(id="main-container"):
            with Vertical(id="games-panel") as games_panel:
                games_panel.border_title = "GAMES"
                yield ListView(
                    *(ListItem(Static(name)) for _, name, _ in GAMES),
                    id="game-list",
                )
            with Vertical(id="preview-panel") as preview_panel:
                preview_panel.border_title = "HOW TO PLAY"
                yield Static(id="preview-art")
                yield Static(id="preview-tagline")
                yield Static("CONTROLS", id="preview-controls-title")
                yield Static(id="preview-controls")
        with Container(id="status-bar"):
            yield Static(id="status-line")
        yield Footer()

    def _banner_text(self) -> str:
        theme = get_theme(self)
        return f"[bold {theme['accent']}]T E R M G A M E S[/]"

    def on_mount(self) -> None:
        game_list = self.query_one("#game-list", ListView)
        game_list.focus()
        self.call_later(lambda: setattr(game_list, "index", 0))
        self._refresh_status()

    def _refresh_status(self) -> None:
        theme = get_theme(self)
        hc = theme["accent"]
        msg = (
            f"[bold {hc}]↑↓[/] [dim]choose[/]   "
            f"[bold {hc}]enter[/] [dim]play[/]   "
            f"[bold {hc}]t[/] [dim]theme[/]   "
            f"[bold {hc}]q[/] [dim]quit[/]"
        )
        self.query_one("#status-line", Static).update(msg)

    @on(ListView.Highlighted, "#game-list")
    def on_game_highlighted(self, event: ListView.Highlighted) -> None:
        self._render_preview(event.list_view.index or 0)

    def _render_preview(self, index: int) -> None:
        game_id, name, _ = GAMES[index]
        info = PREVIEWS[game_id]
        theme = get_theme(self)

        art_lines = info["art"](theme)
        self.query_one("#preview-art", Static).update("\n".join(art_lines))

        self.query_one("#preview-tagline", Static).update(
            f"[bold]{name}[/]  —  {info['tagline']}"
        )

        controls = "\n".join(f"  {line}" for line in info["controls"])
        self.query_one("#preview-controls", Static).update(controls)

    def action_cycle_theme(self) -> None:
        ids = list(THEMES)
        self._active_theme = ids[(ids.index(self._active_theme) + 1) % len(ids)]
        self.query_one("#banner", Static).update(self._banner_text())
        self._refresh_status()
        game_list = self.query_one("#game-list", ListView)
        self._render_preview(game_list.index or 0)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index or 0
        _, _, screen_cls = GAMES[index]
        self.push_screen(screen_cls())


def main() -> None:
    TermGamesApp().run()


if __name__ == "__main__":
    main()
