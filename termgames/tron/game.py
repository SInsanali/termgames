"""Tron — light cycles. Two players, one keyboard.

Controls: P1 steers with wasd, P2 steers with the arrow keys — both leave a
solid trail behind them. Crash into a wall, your own trail, or the other
rider and you're out. space pause, r restart, esc exit.
"""

from __future__ import annotations

from textual.binding import Binding

from ..common.engine import BaseGameScreen, DIRS, OPPOSITE


class TronScreen(BaseGameScreen):
    GAME_ID = "tron"
    GAME_TITLE = "TRON"
    BASE_INTERVAL = 0.11
    BOARD_W = 30
    BOARD_H = 18
    CELL_W = 2

    # Same physical keys as every other game (wasd / arrows / space / r /
    # esc) — here wasd drives player 1 and the arrows drive player 2.
    BINDINGS = [
        Binding("w", "steer_p1('up')", show=False),
        Binding("s", "steer_p1('down')", show=False),
        Binding("a", "steer_p1('left')", show=False),
        Binding("d", "steer_p1('right')", show=False),
        Binding("up", "steer_p2('up')", show=False),
        Binding("down", "steer_p2('down')", show=False),
        Binding("left", "steer_p2('left')", show=False),
        Binding("right", "steer_p2('right')", show=False),
        Binding("space", "toggle_pause", show=False),
        Binding("r", "restart", show=False),
        Binding("escape", "dismiss", show=False),
    ]

    def reset(self) -> None:
        self._score = 0
        w, h = self.BOARD_W, self.BOARD_H
        self._p1 = {"pos": (w // 4, h // 2), "dir": "right", "alive": True, "trail": set()}
        self._p2 = {"pos": (w * 3 // 4, h // 2), "dir": "left", "alive": True, "trail": set()}
        self._p1["trail"].add(self._p1["pos"])
        self._p2["trail"].add(self._p2["pos"])

    def action_steer_p1(self, direction: str) -> None:
        self._steer_player(self._p1, direction)

    def action_steer_p2(self, direction: str) -> None:
        self._steer_player(self._p2, direction)

    def _steer_player(self, player: dict, direction: str) -> None:
        if self._state != "playing":
            return
        if direction == OPPOSITE.get(player["dir"]):
            return
        player["dir"] = direction

    def tick(self) -> None:
        for player in (self._p1, self._p2):
            if not player["alive"]:
                continue
            dx, dy = DIRS[player["dir"]]
            x, y = player["pos"]
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.BOARD_W and 0 <= ny < self.BOARD_H):
                player["alive"] = False
                continue
            if (nx, ny) in self._p1["trail"] or (nx, ny) in self._p2["trail"]:
                player["alive"] = False
                continue
            player["pos"] = (nx, ny)

        if self._p1["alive"]:
            self._p1["trail"].add(self._p1["pos"])
        if self._p2["alive"]:
            self._p2["trail"].add(self._p2["pos"])

        self._score = max(len(self._p1["trail"]), len(self._p2["trail"]))
        if not self._p1["alive"] or not self._p2["alive"]:
            self.game_over()

    def status_line(self) -> str | None:
        return "P1 wasd   P2 arrows"

    def build_frame(self, theme: dict[str, str]) -> list[str]:
        cw = self.CELL_W
        cell = "█" * cw
        p1_trail, p2_trail = self._p1["trail"], self._p2["trail"]
        p1_head, p2_head = self._p1["pos"], self._p2["pos"]
        rows = []
        for y in range(self.BOARD_H):
            line = []
            for x in range(self.BOARD_W):
                cell_pos = (x, y)
                if cell_pos == p1_head:
                    line.append(f"[bold {theme['primary']}]{cell}[/]")
                elif cell_pos == p2_head:
                    line.append(f"[bold {theme['secondary']}]{cell}[/]")
                elif cell_pos in p1_trail:
                    line.append(f"[{theme['primary']}]{cell}[/]")
                elif cell_pos in p2_trail:
                    line.append(f"[{theme['secondary']}]{cell}[/]")
                else:
                    line.append(" " * cw)
            rows.append("".join(line))
        return rows
