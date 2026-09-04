"""Modal prompt for entering a name when a score makes the top-3 leaderboard."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static


class NameEntryScreen(ModalScreen):
    """Prompts for a name; dismisses with it, or None if cancelled."""

    BINDINGS = [Binding("escape", "cancel", "Skip", show=False)]

    CSS = """
    NameEntryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.85);
    }

    #name-entry-container {
        width: 44;
        height: auto;
        background: $surface;
        border: heavy $accent;
        padding: 1 2;
    }

    #name-entry-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    #name-entry-hint {
        text-align: center;
        color: $text-muted;
        padding-top: 1;
    }
    """

    def __init__(self, score: int, rank: int) -> None:
        super().__init__()
        self._score = score
        self._rank = rank

    def compose(self) -> ComposeResult:
        with Vertical(id="name-entry-container"):
            yield Static(f"TOP {self._rank} SCORE — {self._score}!", id="name-entry-title")
            yield Input(placeholder="your name", max_length=12, id="name-entry-input")
            yield Static("[dim]enter[/] save   [dim]esc[/] skip", id="name-entry-hint")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or "???")

    def action_cancel(self) -> None:
        self.dismiss(None)
