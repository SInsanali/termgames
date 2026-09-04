"""termgames — a small collection of terminal games sharing one control
scheme: wasd/arrows to steer, space to pause, r to restart, esc to exit.

Don't run this file directly. Launch the app with the `./termgames` script
at the repo root — it sets up an isolated environment with the right
dependencies and runs this for you.
"""

from __future__ import annotations

import sys

try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.screen import ModalScreen
    from textual.widgets import Footer, ListItem, ListView, Static
except ModuleNotFoundError as exc:
    if exc.name != "textual":
        raise
    print(
        "termgames needs its dependencies installed, which this Python "
        "interpreter doesn't have.\n\n"
        "Run the app with the launcher script from the repo root instead:\n"
        "    ./termgames\n\n"
        "It sets up an isolated environment automatically — no manual pip "
        "install needed.",
        file=sys.stderr,
    )
    sys.exit(1)

from .common import leaderboard
from .common.theme import THEMES, get_theme, load_saved_theme, save_theme
from .snake import SnakeScreen

GAMES = [
    ("snake", "Snake", SnakeScreen),
]


class GameListItem(ListItem):
    """One row in the games list: a '>' marker on the highlighted item,
    same as ViperSSH's list styling."""

    def __init__(self, game_name: str) -> None:
        super().__init__(Static(""))
        self.game_name = game_name

    def on_mount(self) -> None:
        self._redraw()

    def watch_highlighted(self, value: bool) -> None:
        super().watch_highlighted(value)
        self._redraw()

    def refresh_theme(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        theme = get_theme(self.app)
        if self.highlighted:
            self.query_one(Static).update(
                f"[bold {theme['secondary']}]>[/] [bold]{self.game_name}[/]"
            )
        else:
            self.query_one(Static).update(f"  {self.game_name}")


class ThemeListItem(ListItem):
    """One row in the theme picker: a dot marker plus the theme's name,
    and a '>' marker on the highlighted item."""

    def __init__(self, theme_id: str, theme_name: str, is_active: bool) -> None:
        super().__init__(Static(""))
        self.theme_id = theme_id
        self.theme_name = theme_name
        self.is_active = is_active

    def on_mount(self) -> None:
        self._redraw()

    def watch_highlighted(self, value: bool) -> None:
        super().watch_highlighted(value)
        self._redraw()

    def refresh_theme(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        theme = get_theme(self.app)
        marker = f"[bold {theme['primary']}]●[/]" if self.is_active else "[dim]○[/]"
        if self.highlighted:
            self.query_one(Static).update(
                f"[bold {theme['secondary']}]>[/] {marker} [bold]{self.theme_name}[/]"
            )
        else:
            self.query_one(Static).update(f"  {marker} {self.theme_name}")


class ThemeScreen(ModalScreen):
    """Modal theme selector — same interaction as ViperSSH's theme picker."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("t", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    CSS = """
    ThemeScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.85);
    }

    #theme-container {
        width: 44;
        height: auto;
        max-height: 24;
        background: $surface;
        border: heavy $accent;
        padding: 1 2;
    }

    #theme-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    #theme-list {
        height: auto;
        max-height: 16;
    }

    #theme-list > ListItem.-highlight {
        background: $accent-darken-3;
    }

    #theme-hint {
        text-align: center;
        color: $text-muted;
        padding-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="theme-container"):
            yield Static("SELECT THEME", id="theme-title")
            yield ListView(id="theme-list")
            yield Static("[dim]enter[/] apply   [dim]esc[/] close", id="theme-hint")

    def on_mount(self) -> None:
        theme_list = self.query_one("#theme-list", ListView)
        current = self.app._active_theme
        for theme_id, theme in THEMES.items():
            theme_list.append(ThemeListItem(theme_id, theme["name"], theme_id == current))
        theme_list.focus()
        self.call_later(lambda: setattr(theme_list, "index", list(THEMES).index(current)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        event.stop()
        if isinstance(event.item, ThemeListItem):
            self.dismiss(event.item.theme_id)


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

    #leaderboard-panel {
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

    #game-list > ListItem.-highlight {
        background: $success-darken-3;
        color: $text;
    }

    #leaderboard-body {
        height: auto;
        padding: 1 2;
    }

    #status-bar {
        dock: bottom;
        height: 3;
        padding: 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("t", "open_themes", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    _active_theme = "viper"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._active_theme = load_saved_theme()

    def get_css_variables(self) -> dict[str, str]:
        """Map the active theme's colors onto Textual's built-in CSS
        variables, so every panel/border/highlight in our CSS (which is
        written against $success/$error/$accent/etc.) follows the theme
        automatically — same approach as ViperSSH."""
        variables = super().get_css_variables()
        theme = get_theme(self)
        variables["background"] = theme["bg"]
        variables["surface"] = theme.get("panel_bg", theme["bg"])
        variables["success"] = theme["primary"]
        variables["error"] = theme["secondary"]
        variables["accent"] = theme["accent"]
        return variables

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
                    *(GameListItem(name) for _, name, _ in GAMES),
                    id="game-list",
                )
            with Vertical(id="leaderboard-panel") as leaderboard_panel:
                leaderboard_panel.border_title = "LEADERBOARD"
                yield Static(id="leaderboard-body")
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
        self._render_leaderboard(event.list_view.index or 0)

    def _render_leaderboard(self, index: int) -> None:
        game_id, name, _ = GAMES[index]
        theme = get_theme(self)
        board = leaderboard.load(game_id)

        lines = [f"[bold]{name}[/]", ""]
        if not board:
            lines.append("[dim]No scores yet — be the first![/]")
        else:
            for i, entry in enumerate(board):
                rank = i + 1
                color = theme["accent"] if rank == 1 else theme["primary"]
                lines.append(
                    f"[bold {color}]{rank}.[/] {entry['name']:<12} "
                    f"[bold]{entry['score']:>6}[/]"
                )
        self.query_one("#leaderboard-body", Static).update("\n".join(lines))

    def action_open_themes(self) -> None:
        def handle_theme(theme_id: str | None) -> None:
            if theme_id and theme_id != self._active_theme:
                self._active_theme = theme_id
                save_theme(theme_id)

                # Recompute the stylesheet (get_css_variables) against the
                # new theme — panel borders, highlight backgrounds, etc.
                self.call_later(self.refresh_css)

                self.query_one("#banner", Static).update(self._banner_text())
                self._refresh_status()
                game_list = self.query_one("#game-list", ListView)
                self._render_leaderboard(game_list.index or 0)

                # Markup baked into list-item labels isn't touched by a CSS
                # refresh, so re-render each item's own themed text directly.
                for item in self.query(ListItem):
                    refresh = getattr(item, "refresh_theme", None)
                    if callable(refresh):
                        refresh()

                self.notify(f"Theme: {THEMES[theme_id]['name']}", timeout=2)

        self.push_screen(ThemeScreen(), handle_theme)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index or 0
        _, _, screen_cls = GAMES[index]

        def after_game(_: object) -> None:
            self._render_leaderboard(index)

        self.push_screen(screen_cls(), after_game)


def main() -> None:
    TermGamesApp().run()


if __name__ == "__main__":
    main()
