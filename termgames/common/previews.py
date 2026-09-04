"""Static preview art + blurbs shown in the launcher's right-hand panel.

Each entry is a small mock "screenshot" (Rich-markup rows, themed at render
time) plus a one-line tagline and a short list of how-to-play bullets.
"""

from __future__ import annotations

from typing import Callable

PreviewArt = Callable[[dict[str, str]], list[str]]


def _tetris_art(t: dict[str, str]) -> list[str]:
    p, s, a = t["primary"], t["secondary"], t["accent"]
    b = " "
    return [
        f"{b*7}[{a}]██[/]{b*9}",
        f"{b*7}[{a}]██[/]{b*9}",
        f"{b*5}[{a}]██████[/]{b*7}",
        f"{b*2}[{p}]██[/]{b*2}[{p}]██[/][{s}]██[/]{b*2}[{p}]██[/]{b*2}[{p}]██[/]",
        f"[{p}]██[/][{p}]██[/][{s}]██[/][{s}]██[/][{p}]██[/][{p}]██[/][{s}]██[/][{p}]██[/][{p}]██[/]",
        f"[{s}]██[/][{p}]██[/][{p}]██[/][{s}]██[/][{s}]██[/][{p}]██[/][{p}]██[/][{s}]██[/][{p}]██[/]",
    ]


def _2048_art(t: dict[str, str]) -> list[str]:
    p, s, a = t["primary"], t["secondary"], t["accent"]
    row = lambda c1, c2, v1, v2: (
        f"[bold white on {c1}] {v1:^4}[/] [bold white on {c2}] {v2:^4}[/]"
    )
    return [
        row(p, s, "2", "4"),
        f"",
        row(s, a, "8", "2"),
        f"",
        row(p, p, "4", "2"),
    ]


def _breakout_art(t: dict[str, str]) -> list[str]:
    p, s, a = t["primary"], t["secondary"], t["accent"]
    brick = lambda c: f"[{c}]██[/]" * 6
    return [
        brick(s),
        brick(s),
        "",
        "",
        f"{' '*4}[{a}]██[/]",
        "",
        f"{' '*2}[{p}]████████[/]",
    ]


def _pong_art(t: dict[str, str]) -> list[str]:
    p, s, a = t["primary"], t["secondary"], t["accent"]
    dim = "[dim]┊[/]"
    return [
        f"[{p}]█[/]{' '*7}{dim}{' '*7}[{s}]█[/]",
        f"[{p}]█[/]{' '*7}{dim}{' '*7}[{s}]█[/]",
        f"{' '*7}[{a}]█[/]{dim}",
        f"[{p}]█[/]{' '*7}{dim}{' '*7}[{s}]█[/]",
        f"[{p}]█[/]{' '*7}{dim}{' '*7}[{s}]█[/]",
    ]


def _tron_art(t: dict[str, str]) -> list[str]:
    p, s = t["primary"], t["secondary"]
    return [
        f"[{p}]████[/]{' '*8}",
        f"{' '*3}[{p}]██[/]{' '*9}",
        f"{' '*3}[{p}]██[/]{' '*4}[{s}]████[/]",
        f"{' '*3}[{p}]██[/]{' '*8}[{s}]██[/]",
        f"{' '*3}[{p}]██████[/]{' '*3}[{s}]██[/]",
    ]


PREVIEWS: dict[str, dict] = {
    "tetris": {
        "tagline": "Stack falling blocks, clear full rows.",
        "controls": [
            "a / d  or  left / right  — move",
            "w  or  up  — rotate",
            "s  or  down  — soft drop",
        ],
        "art": _tetris_art,
    },
    "2048": {
        "tagline": "Slide tiles, merge matching numbers, reach 2048.",
        "controls": [
            "wasd / arrows — slide the whole board",
            "turn-based — no clock to race",
        ],
        "art": _2048_art,
    },
    "breakout": {
        "tagline": "Bounce the ball, clear every brick.",
        "controls": [
            "a / d  or  left / right  — move paddle",
            "ball launches and moves on its own",
        ],
        "art": _breakout_art,
    },
    "pong": {
        "tagline": "Rally against the CPU for as long as you can.",
        "controls": [
            "w / s  or  up / down  — move paddle",
            "score = rally length before a miss",
        ],
        "art": _pong_art,
    },
    "tron": {
        "tagline": "Two riders, one keyboard, no second chances.",
        "controls": [
            "P1: wasd — P2: arrow keys",
            "leave a solid trail — don't hit a wall or a trail",
        ],
        "art": _tron_art,
    },
}
