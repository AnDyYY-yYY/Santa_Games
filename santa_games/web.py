"""Flask app serving a modern web UI for the Santa delivery game."""

from __future__ import annotations

import argparse
import os
from typing import Dict, Tuple

from flask import Flask, jsonify, render_template, request, session

from .game import SantaGame

SESSION_KEY = "santa_game_state"


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.secret_key = os.environ.get("SANTA_SECRET_KEY", "dev-santa-secret")

    @app.route("/")
    def index():
        ensure_game()
        return render_template("index.html")

    @app.route("/api/state", methods=["GET"])
    def state():
        game, payload = ensure_game()
        payload["message"] = "Welcome back!" if game.moves else "Use the controls to start moving."
        return jsonify(payload)

    @app.route("/api/new", methods=["POST"])
    def new_game():
        game = SantaGame()
        session[SESSION_KEY] = game.to_dict()
        return jsonify(game_payload(game, message="New game started! 🎁"))

    @app.route("/api/move", methods=["POST"])
    def move():
        game, _ = ensure_game()
        data = request.get_json(silent=True) or {}
        direction = str(data.get("direction", "")).lower()
        result = game.move(direction)
        session[SESSION_KEY] = game.to_dict()
        return jsonify(game_payload(game, message=result))

    return app


def ensure_game() -> Tuple[SantaGame, Dict]:
    if SESSION_KEY not in session:
        session[SESSION_KEY] = SantaGame().to_dict()
    game = SantaGame.from_dict(session[SESSION_KEY])
    return game, game_payload(game)


def game_payload(game: SantaGame, message: str | None = None) -> Dict:
    return {
        "board": game.board_cells(),
        "status": game.status(),
        "isWon": game.is_won,
        "isLost": game.is_lost,
        "moves": game.moves,
        "maxMoves": game.max_moves,
        "remainingMoves": game.remaining_moves,
        "bag": game.bag,
        "delivered": game.delivered,
        "winsAt": getattr(game, "_wins_at", len(game.gifts)),
        "history": game.history,
        "message": message or "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Santa Delivery Game web server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    parser.add_argument("--port", default=8000, type=int, help="Port to serve on (default: 8000)")
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
