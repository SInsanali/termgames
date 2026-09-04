"""Tetris — falling blocks.

Controls: left/right (a/d or arrows) move, up (w) rotate, down (s) soft-drop,
space pause, r restart, esc exit.
"""

from __future__ import annotations

import random

from ..common.engine import BaseGameScreen

# Each piece: 4 rotation states, each a list of (x, y) offsets in a 4x4 box.
PIECES: dict[str, list[list[tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}
PIECE_KEYS = list(PIECES)


class TetrisScreen(BaseGameScreen):
    GAME_ID = "tetris"
    GAME_TITLE = "TETRIS"
    BASE_INTERVAL = 0.5
    MIN_INTERVAL = 0.1
    BOARD_W = 12
    BOARD_H = 18
    CELL_W = 2

    def reset(self) -> None:
        self._grid: list[list[bool]] = [[False] * self.BOARD_W for _ in range(self.BOARD_H)]
        self._score = 0
        self._lines = 0
        self._spawn()

    def _spawn(self) -> None:
        self._piece = random.choice(PIECE_KEYS)
        self._rot = 0
        self._px = self.BOARD_W // 2 - 2
        self._py = 0
        if self._collides(self._px, self._py, self._rot):
            self.game_over()

    def _cells(self, rot: int) -> list[tuple[int, int]]:
        return PIECES[self._piece][rot % 4]

    def _collides(self, px: int, py: int, rot: int) -> bool:
        for ox, oy in self._cells(rot):
            x, y = px + ox, py + oy
            if x < 0 or x >= self.BOARD_W or y >= self.BOARD_H:
                return True
            if y >= 0 and self._grid[y][x]:
                return True
        return False

    def _lock(self) -> None:
        for ox, oy in self._cells(self._rot):
            x, y = self._px + ox, self._py + oy
            if 0 <= y < self.BOARD_H:
                self._grid[y][x] = True
        cleared = 0
        y = self.BOARD_H - 1
        while y >= 0:
            if all(self._grid[y]):
                del self._grid[y]
                self._grid.insert(0, [False] * self.BOARD_W)
                cleared += 1
            else:
                y -= 1
        if cleared:
            self._lines += cleared
            self._score += (100, 300, 500, 800)[min(cleared, 4) - 1]
            self.respeed(per_point=0.0015)
        self._spawn()

    def tick(self) -> None:
        if not self._collides(self._px, self._py + 1, self._rot):
            self._py += 1
        else:
            self._lock()

    def steer(self, direction: str) -> None:
        if direction == "left" and not self._collides(self._px - 1, self._py, self._rot):
            self._px -= 1
        elif direction == "right" and not self._collides(self._px + 1, self._py, self._rot):
            self._px += 1
        elif direction == "down":
            if not self._collides(self._px, self._py + 1, self._rot):
                self._py += 1
                self._score += 1
            else:
                self._lock()
        elif direction == "up":
            new_rot = (self._rot + 1) % 4
            if not self._collides(self._px, self._py, new_rot):
                self._rot = new_rot

    def status_line(self) -> str | None:
        return f"lines {self._lines}   wasd move/rotate   s soft-drop"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        cw = self.CELL_W
        cell = "█" * cw
        active = set()
        for ox, oy in self._cells(self._rot):
            active.add((self._px + ox, self._py + oy))

        rows = []
        for y in range(self.BOARD_H):
            line = []
            for x in range(self.BOARD_W):
                if (x, y) in active:
                    line.append(f"[{theme['accent']}]{cell}[/]")
                elif self._grid[y][x]:
                    line.append(f"[{theme['primary']}]{cell}[/]")
                else:
                    line.append(" " * cw)
            rows.append("".join(line))
        return rows
