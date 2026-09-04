"""Breakout — bounce the ball, clear the bricks.

Controls: left/right (a/d or arrows) move the paddle, space pause, r restart,
esc exit.
"""

from __future__ import annotations

from ..common.engine import BaseGameScreen

PADDLE_W = 6
BRICK_ROWS = 4


class BreakoutScreen(BaseGameScreen):
    GAME_ID = "breakout"
    GAME_TITLE = "BREAKOUT"
    BASE_INTERVAL = 0.09
    MIN_INTERVAL = 0.04
    BOARD_W = 24
    BOARD_H = 18
    CELL_W = 2

    def reset(self) -> None:
        self._score = 0
        self._paddle_x = self.BOARD_W // 2 - PADDLE_W // 2
        self._ball = [self.BOARD_W // 2, self.BOARD_H - 3]
        self._bvel = [1, -1]
        self._bricks = {
            (x, y) for y in range(2, 2 + BRICK_ROWS) for x in range(self.BOARD_W)
        }

    def steer(self, direction: str) -> None:
        if direction == "left":
            self._paddle_x = max(0, self._paddle_x - 2)
        elif direction == "right":
            self._paddle_x = min(self.BOARD_W - PADDLE_W, self._paddle_x + 2)

    def tick(self) -> None:
        bx, by = self._ball
        dx, dy = self._bvel
        nx, ny = bx + dx, by + dy

        if nx <= 0 or nx >= self.BOARD_W - 1:
            dx = -dx
            nx = bx + dx
        if ny <= 0:
            dy = -dy
            ny = by + dy

        if (nx, ny) in self._bricks:
            self._bricks.discard((nx, ny))
            dy = -dy
            ny = by + dy
            self._score += 1
            self.respeed(per_point=0.0008)
            if not self._bricks:
                self.game_over()
                return
        elif ny == self.BOARD_H - 2 and self._paddle_x <= nx < self._paddle_x + PADDLE_W:
            dy = -1
            offset = nx - (self._paddle_x + PADDLE_W // 2)
            dx = 1 if offset > 0 else -1 if offset < 0 else dx
            ny = by + dy
        elif ny >= self.BOARD_H - 1:
            self.game_over()
            return

        self._ball = [nx, ny]
        self._bvel = [dx, dy]

    def status_line(self) -> str | None:
        return f"bricks left {len(self._bricks)}"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        cw = self.CELL_W
        cell = "█" * cw
        bx, by = self._ball
        rows = []
        for y in range(self.BOARD_H):
            line = []
            for x in range(self.BOARD_W):
                if (x, y) == (bx, by):
                    line.append(f"[{theme['accent']}]{cell}[/]")
                elif (x, y) in self._bricks:
                    line.append(f"[{theme['secondary']}]{cell}[/]")
                elif y == self.BOARD_H - 2 and self._paddle_x <= x < self._paddle_x + PADDLE_W:
                    line.append(f"[{theme['primary']}]{cell}[/]")
                else:
                    line.append(" " * cw)
            rows.append("".join(line))
        return rows
