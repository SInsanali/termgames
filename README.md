# termgames

A small collection of terminal games built with [Textual](https://github.com/Textualize/textual),
all sharing one control scheme so switching games never means relearning
the keys:

| Key            | Action                          |
|----------------|----------------------------------|
| `w a s d` / arrows | steer / move                |
| `space`        | pause / resume                  |
| `r`            | restart (while paused or over)  |
| `esc`          | exit to the menu                |

## Games

- **Tetris** — wasd/arrows move and rotate, `s` soft-drops.
- **2048** — wasd/arrows slide the whole board.
- **Breakout** — `a`/`d` or left/right move the paddle.
- **Pong** — `w`/`s` or up/down move your paddle against the CPU.
- **Tron** — two players, one keyboard: P1 uses wasd, P2 uses the arrow keys.

High scores persist per-game to `~/.termgames/scores/`.

## Install & run

```bash
pip install -e .
termgames
```

or, without installing:

```bash
python -m termgames
```

## Adding a game

Every game is a `BaseGameScreen` subclass (see `termgames/common/engine.py`)
that implements three methods:

- `reset()` — set up a fresh board/score
- `tick()` — advance one step of the game clock
- `build_frame(theme)` — return the board's rows as Rich-markup strings

The base class handles input bindings, the pause/game-over state machine,
themed borders, and high-score persistence, so a new game is just its grid
logic. Drop the new package under `termgames/`, add it to `GAMES` in
`termgames/main.py`, and it shows up in the launcher menu.
