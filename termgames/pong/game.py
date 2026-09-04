"""Pong — rally against the CPU.

Controls: up/down (w/s or arrows) move your paddle, space pause, r restart,
esc exit. Miss the ball and it's game over; your score is your rally count.
"""

from __future__ import annotations

import random

from ..common.engine import BaseGameScreen

PADDLE_H = 4


class PongScreen(BaseGameScreen):
    GAME_ID = "pong"
    GAME_TITLE = "PONG"
    BASE_INTERVAL = 0.09
    MIN_INTERVAL = 0.045
    BOARD_W = 30
    BOARD_H = 18
    CELL_W = 1

    def reset(self) -> None:
        self._score = 0
        self._player_y = self.BOARD_H // 2 - PADDLE_H // 2
        self._cpu_y = self.BOARD_H // 2 - PADDLE_H // 2
        self._pdir = 0
        self._reset_ball()

    def _reset_ball(self) -> None:
        self._ball = [self.BOARD_W // 2, self.BOARD_H // 2]
        self._bvel = [random.choice([-1, 1]), random.choice([-1, 1])]

    def steer(self, direction: str) -> None:
        if direction == "up":
            self._pdir = -1
        elif direction == "down":
            self._pdir = 1

    def tick(self) -> None:
        self._player_y = max(0, min(self.BOARD_H - PADDLE_H, self._player_y + self._pdir))

        target = self._ball[1] - PADDLE_H // 2
        if self._cpu_y < target:
            self._cpu_y = min(self.BOARD_H - PADDLE_H, self._cpu_y + 1)
        elif self._cpu_y > target:
            self._cpu_y = max(0, self._cpu_y - 1)

        bx, by = self._ball
        dx, dy = self._bvel
        nx, ny = bx + dx, by + dy

        if ny <= 0 or ny >= self.BOARD_H - 1:
            dy = -dy
            ny = by + dy

        if nx <= 1 and self._player_y <= ny < self._player_y + PADDLE_H:
            dx = 1
            nx = bx + dx
        elif nx <= 0:
            self.game_over()
            return

        if nx >= self.BOARD_W - 2 and self._cpu_y <= ny < self._cpu_y + PADDLE_H:
            dx = -1
            nx = bx + dx
            self._score += 1
            self.respeed(per_point=0.001)
        elif nx >= self.BOARD_W - 1:
            self._reset_ball()
            return

        self._ball = [nx, ny]
        self._bvel = [dx, dy]

    def status_line(self) -> str | None:
        return "w/s or up/down to move"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        bx, by = self._ball
        rows = []
        for y in range(self.BOARD_H):
            line = []
            for x in range(self.BOARD_W):
                if (x, y) == (bx, by):
                    line.append(f"[{theme['accent']}]█[/]")
                elif x == 1 and self._player_y <= y < self._player_y + PADDLE_H:
                    line.append(f"[{theme['primary']}]█[/]")
                elif x == self.BOARD_W - 2 and self._cpu_y <= y < self._cpu_y + PADDLE_H:
                    line.append(f"[{theme['secondary']}]█[/]")
                elif x == self.BOARD_W // 2:
                    line.append("[dim]┊[/]")
                else:
                    line.append(" ")
            rows.append("".join(line))
        return rows
