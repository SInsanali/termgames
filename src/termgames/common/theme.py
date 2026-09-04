"""Color palettes shared by every game.

Each theme maps a handful of semantic roles (primary piece color, accent/UI
color, secondary/danger color, background) so games render consistently and
can be reskinned without touching game logic.
"""

THEMES: dict[str, dict[str, str]] = {
    "viper": {
        "primary": "#39ff6a",
        "secondary": "#ff4d4d",
        "accent": "#39d0ff",
        "bg": "#0b0f0c",
    },
    "amber": {
        "primary": "#ffb000",
        "secondary": "#ff5f3f",
        "accent": "#ffe08a",
        "bg": "#120c04",
    },
    "mono": {
        "primary": "#e8e8e8",
        "secondary": "#8a8a8a",
        "accent": "#ffffff",
        "bg": "#0a0a0a",
    },
    "synth": {
        "primary": "#ff2fd0",
        "secondary": "#2fe6ff",
        "accent": "#f7ff2f",
        "bg": "#0c0620",
    },
}

DEFAULT_THEME = "viper"


def get_theme(app=None) -> dict[str, str]:
    """Return the active theme dict, falling back to the default."""
    theme_id = getattr(app, "_active_theme", DEFAULT_THEME) if app else DEFAULT_THEME
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])
