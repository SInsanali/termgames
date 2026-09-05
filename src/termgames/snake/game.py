"""Snake — the original ViperSSH easter egg, now a first-class game here.

Controls: wasd/arrows steer, space pause, r restart, esc exit. The snake
speeds up as it grows, and can't reverse directly into itself.
"""

from __future__ import annotations

import random
from collections import deque

from textual.color import Color

from ..common.engine import BaseGameScreen, DIRS, OPPOSITE


class SnakeScreen(BaseGameScreen):
    GAME_ID = "snake"
    GAME_TITLE = "SNAKE"
    BASE_INTERVAL = 0.13
    MIN_INTERVAL = 0.05

    # Fallback only — _autosize() overrides these at game start. Chunkier
    # cells (4 wide x 2 tall, vs. the engine default 2x1) so a short snake
    # reads as big blocks rather than getting lost in a sea of tiny ones.
    BOARD_W = 34
    BOARD_H = 20
    CELL_W = 4
    CELL_H = 2
    MIN_BOARD_W = 12
    MAX_BOARD_W = 60
    MIN_BOARD_H = 6
    MAX_BOARD_H = 26

    def reset(self) -> None:
        self._score = 0
        cx, cy = self.BOARD_W // 2, self.BOARD_H // 2
        self._snake: deque = deque([(cx - 2, cy), (cx - 1, cy), (cx, cy)])  # head = last
        self._dir = self._pending = "right"
        self._place_food()

    def _place_food(self) -> None:
        occupied = set(self._snake)
        empty = [
            (x, y)
            for x in range(self.BOARD_W)
            for y in range(self.BOARD_H)
            if (x, y) not in occupied
        ]
        self._food = random.choice(empty) if empty else None

    def steer(self, direction: str) -> None:
        if direction == OPPOSITE.get(self._dir) and len(self._snake) > 1:
            return
        self._pending = direction

    def tick(self) -> None:
        self._dir = self._pending
        hx, hy = self._snake[-1]
        dx, dy = DIRS[self._dir]
        nx, ny = hx + dx, hy + dy

        if not (0 <= nx < self.BOARD_W and 0 <= ny < self.BOARD_H):
            self.game_over()
            return

        eating = (nx, ny) == self._food
        body = set(self._snake)
        if not eating:
            body.discard(self._snake[0])  # tail vacates this step
        if (nx, ny) in body:
            self.game_over()
            return

        self._snake.append((nx, ny))
        if eating:
            self._score += 1
            self._place_food()
            self.respeed()
        else:
            self._snake.popleft()

    def status_line(self) -> str | None:
        return "wasd / arrows steer"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        cw = self.CELL_W
        cell = "█" * cw
        head_color = Color.parse(theme["primary"]).blend(Color.parse("#ffffff"), 0.5).hex
        snake_body = set(self._snake)
        head = self._snake[-1]

        rows = []
        for y in range(self.BOARD_H):
            line = []
            for x in range(self.BOARD_W):
                if (x, y) == head:
                    line.append(f"[{head_color}]{cell}[/]")
                elif (x, y) in snake_body:
                    line.append(f"[{theme['primary']}]{cell}[/]")
                elif (x, y) == self._food:
                    line.append(f"[{theme['secondary']}]{cell}[/]")
                else:
                    line.append(" " * cw)
            rows.append("".join(line))
        return rows
