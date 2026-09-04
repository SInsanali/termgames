"""2048 — slide tiles, merge matching numbers.

Controls: wasd / arrows slide the whole board, space pause, r restart,
esc exit. Turn-based (no timer pressure).
"""

from __future__ import annotations

import random

from textual.color import Color

from ..common.engine import BaseGameScreen

SIZE = 4


def _slide_merge(row: list[int]) -> tuple[list[int], int]:
    """Slide a single row left, merging equal neighbors. Returns (row, gained)."""
    vals = [v for v in row if v]
    merged: list[int] = []
    gained = 0
    i = 0
    while i < len(vals):
        if i + 1 < len(vals) and vals[i] == vals[i + 1]:
            merged.append(vals[i] * 2)
            gained += vals[i] * 2
            i += 2
        else:
            merged.append(vals[i])
            i += 1
    merged += [0] * (len(row) - len(merged))
    return merged, gained


class TwentyFortyEightScreen(BaseGameScreen):
    GAME_ID = "2048"
    GAME_TITLE = "2048"
    BASE_INTERVAL = 1.0
    BOARD_W = SIZE
    BOARD_H = SIZE * 3   # 3 display rows per grid row
    CELL_W = 6

    def reset(self) -> None:
        self._grid = [[0] * SIZE for _ in range(SIZE)]
        self._score = 0
        self._spawn_tile()
        self._spawn_tile()

    def _spawn_tile(self) -> None:
        empties = [(x, y) for y in range(SIZE) for x in range(SIZE) if not self._grid[y][x]]
        if not empties:
            return
        x, y = random.choice(empties)
        self._grid[y][x] = 4 if random.random() < 0.1 else 2

    def tick(self) -> None:
        pass  # 2048 is move-driven, not timer-driven

    def _rotate_to_left(self, direction: str) -> list[list[int]]:
        """Return the grid rotated so `direction` faces left, for reuse of slide-left."""
        g = self._grid
        if direction == "left":
            return [row[:] for row in g]
        if direction == "right":
            return [row[::-1] for row in g]
        if direction == "up":
            return [[g[y][x] for y in range(SIZE)] for x in range(SIZE)]
        # down
        return [[g[SIZE - 1 - y][x] for y in range(SIZE)] for x in range(SIZE)]

    def _rotate_from_left(self, grid: list[list[int]], direction: str) -> list[list[int]]:
        if direction == "left":
            return grid
        if direction == "right":
            return [row[::-1] for row in grid]
        if direction == "up":
            return [[grid[x][y] for x in range(SIZE)] for y in range(SIZE)]
        # down
        return [[grid[SIZE - 1 - x][y] for x in range(SIZE)] for y in range(SIZE)]

    def steer(self, direction: str) -> None:
        working = self._rotate_to_left(direction)
        changed = False
        gained = 0
        new_rows = []
        for row in working:
            new_row, g = _slide_merge(row)
            if new_row != row:
                changed = True
            gained += g
            new_rows.append(new_row)
        if not changed:
            return
        self._grid = self._rotate_from_left(new_rows, direction)
        self._score += gained
        self._spawn_tile()
        if not self._any_moves_left():
            self.game_over()

    def _any_moves_left(self) -> bool:
        for y in range(SIZE):
            for x in range(SIZE):
                if self._grid[y][x] == 0:
                    return True
                if x + 1 < SIZE and self._grid[y][x] == self._grid[y][x + 1]:
                    return True
                if y + 1 < SIZE and self._grid[y][x] == self._grid[y + 1][x]:
                    return True
        return False

    def status_line(self) -> str | None:
        return "wasd / arrows slide"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        width = self.BOARD_W * self.CELL_W
        primary = Color.parse(theme["primary"])
        secondary = Color.parse(theme["secondary"])
        rows: list[str] = []
        for gy in range(SIZE):
            top, mid, bot = [], [], []
            for gx in range(SIZE):
                value = self._grid[gy][gx]
                if value:
                    frac = min(1.0, (value.bit_length() - 1) / 11)
                    color = primary.blend(secondary, frac).hex
                    label = str(value).center(self.CELL_W)
                    mid.append(f"[bold white on {color}]{label}[/]")
                    top.append(f"[on {color}]{' ' * self.CELL_W}[/]")
                    bot.append(f"[on {color}]{' ' * self.CELL_W}[/]")
                else:
                    blank = " " * self.CELL_W
                    top.append(blank)
                    mid.append(blank)
                    bot.append(blank)
            rows.append("".join(top))
            rows.append("".join(mid))
            rows.append("".join(bot))
        return rows
