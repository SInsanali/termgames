"""Color palettes shared by every game — the same theme set and colors as
ViperSSH, so switching between the two feels like the same toolkit.

Each theme maps ``primary``/``secondary``/``accent``/``bg`` (ViperSSH's
env_color/host_color/accent/bg) so games render consistently and can be
reskinned without touching game logic.
"""

from pathlib import Path

THEMES: dict[str, dict[str, str]] = {
    "viper": {
        "name": "Viper (Default)",
        "bg": "#0a0a0a",
        "panel_bg": "#0d0d0d",
        "primary": "#00ff00",
        "secondary": "#ff0000",
        "accent": "#ff00ff",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "bg": "#0a0a12",
        "panel_bg": "#12121f",
        "primary": "#0ff0fc",
        "secondary": "#ff2a6d",
        "accent": "#d1f700",
    },
    "sunset": {
        "name": "Sunset",
        "bg": "#1a0a0a",
        "panel_bg": "#2d0d0d",
        "primary": "#ff6600",
        "secondary": "#ffcc00",
        "accent": "#ff0066",
    },
    "matrix": {
        "name": "Matrix",
        "bg": "#000000",
        "panel_bg": "#001100",
        "primary": "#00ff00",
        "secondary": "#00dd00",
        "accent": "#00ff00",
    },
    "blaze": {
        "name": "Blaze",
        "bg": "#120c08",
        "panel_bg": "#1e1410",
        "primary": "#ff6b6b",
        "secondary": "#bf5af2",
        "accent": "#fbbf24",
    },
    "dracula": {
        "name": "Dracula",
        "bg": "#282a36",
        "panel_bg": "#44475a",
        "primary": "#50fa7b",
        "secondary": "#ff79c6",
        "accent": "#f1fa8c",
    },
    "onedark": {
        "name": "One Dark",
        "bg": "#282c34",
        "panel_bg": "#3e4451",
        "primary": "#98c379",
        "secondary": "#e06c75",
        "accent": "#61afef",
    },
    "monokai": {
        "name": "Monokai",
        "bg": "#272822",
        "panel_bg": "#3e3d32",
        "primary": "#a6e22e",
        "secondary": "#f92672",
        "accent": "#e6db74",
    },
    "ember": {
        "name": "Ember",
        "bg": "#1a0e0a",
        "panel_bg": "#261612",
        "primary": "#ff9f43",
        "secondary": "#ee5a24",
        "accent": "#ffd32a",
    },
    "gruvbox": {
        "name": "Gruvbox",
        "bg": "#282828",
        "panel_bg": "#3c3836",
        "primary": "#b8bb26",
        "secondary": "#fb4934",
        "accent": "#fabd2f",
    },
    "aurora": {
        "name": "Aurora",
        "bg": "#070e1a",
        "panel_bg": "#0e1a2b",
        "primary": "#45ffbc",
        "secondary": "#c850c0",
        "accent": "#4facfe",
    },
    "midnight": {
        "name": "Midnight",
        "bg": "#0d0f18",
        "panel_bg": "#151929",
        "primary": "#82aaff",
        "secondary": "#c792ea",
        "accent": "#89ddff",
    },
    "jade": {
        "name": "Jade",
        "bg": "#0a120e",
        "panel_bg": "#12201a",
        "primary": "#36d399",
        "secondary": "#fbbd23",
        "accent": "#66cc8a",
    },
}

DEFAULT_THEME = "viper"

THEME_FILE = Path.home() / ".termgames" / "theme"


def get_theme(app=None) -> dict[str, str]:
    """Return the active theme dict, falling back to the default."""
    theme_id = getattr(app, "_active_theme", DEFAULT_THEME) if app else DEFAULT_THEME
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])


def load_saved_theme() -> str:
    try:
        theme_id = THEME_FILE.read_text().strip()
    except OSError:
        return DEFAULT_THEME
    return theme_id if theme_id in THEMES else DEFAULT_THEME


def save_theme(theme_id: str) -> None:
    try:
        THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        THEME_FILE.write_text(theme_id)
    except OSError:
        pass
