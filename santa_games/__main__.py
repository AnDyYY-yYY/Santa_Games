"""Command-line entry point for the Santa delivery game."""

from __future__ import annotations

import sys
from typing import Iterable

from .game import SantaGame


def _print_intro(game: SantaGame) -> None:
    print("🎅 Welcome to Santa's Delivery Run!")
    print(
        "Collect all gifts and deliver them to every house before you run out of moves."
    )
    print(game.help_text())
    print()
    _print_map(game)


def _print_map(game: SantaGame) -> None:
    print("Current map:")
    print(game.render())
    print(game.status())


def _prompt(commands: Iterable[str]) -> str:
    return input(f"\nEnter move ({', '.join(commands)}): ").strip().lower()


def run() -> int:
    game = SantaGame()
    _print_intro(game)

    while not game.is_over:
        cmd = _prompt(["N", "S", "E", "W", "LOOK", "STATUS", "QUIT"])
        if cmd in {"quit", "q"}:
            print("Thanks for playing! Goodbye.")
            return 0
        if cmd in {"look", "l"}:
            _print_map(game)
            continue
        if cmd in {"status"}:
            print(game.status())
            continue

        if cmd in {"n", "s", "e", "w"}:
            result = game.move(cmd)
            print(result)
            _print_map(game)
            continue

        print("Sorry, I don't know that command. Try N, S, E, or W.")

    print(game.status())
    return 0


if __name__ == "__main__":
    sys.exit(run())
