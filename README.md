# Santa Games

A tiny, text-based Santa delivery game playable from the terminal.

## Play in the browser

Open the modern UI with a simple static server:

```bash
cd web
python -m http.server 8000
```

Then visit http://localhost:8000 to play. Use arrow keys or WASD to move, grab gifts and
cocoa, slide on ice, and deliver everything to the houses before you run out of moves.

## How to play

```bash
python -m santa_games
```

Use `N`, `S`, `E`, or `W` to move. Collect gifts (`G`) and deliver them to houses (`H`)
before you run out of moves. `LOOK` shows the map again and `STATUS` summarizes your
progress.

## Running tests

```bash
pytest
```
