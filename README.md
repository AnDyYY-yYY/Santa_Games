# Santa Games

A cozy Santa delivery game—now with a modern web UI and the original terminal mode.

## Play in the browser

1) Install dependencies
```bash
pip install -r requirements.txt
```
2) Start the web server
```bash
python -m santa_games.web --port 8000
```
3) Open http://localhost:8000 and use the on-screen controls (or WASD/arrow keys) to move.

## Play in the terminal

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
