import pytest

from santa_games import SantaGame


def test_initial_state_has_expected_counts():
    game = SantaGame()
    assert game.bag == 0
    assert game.delivered == 0
    assert len(game.gifts) == 3
    assert len(game.houses) == 3


def test_collecting_gift_increases_bag():
    game = SantaGame()
    # Move east to collect first gift
    game.move("e")
    game.move("e")
    game.move("e")
    assert game.bag == 1
    assert len(game.gifts) == 2


def test_delivery_to_house_empts_bag_and_increments_delivered():
    game = SantaGame()
    # Grab gift east, then head to the house on row 1, col 7 (0-indexed)
    game.move("e")
    game.move("e")
    game.move("e")  # gift
    game.move("e")
    game.move("e")
    game.move("e")  # house
    assert game.bag == 0
    assert game.delivered == 1


def test_cannot_walk_through_walls():
    game = SantaGame()
    result = game.move("n")
    assert "snowbank" in result.lower()
    assert game.moves == 0  # Move should not count


def test_victory_when_all_gifts_delivered():
    game = SantaGame()
    # Collect and deliver all gifts along a deterministic path
    path = ["e", "e", "e", "e", "e", "e"]  # first gift + house
    path += [
        "w",
        "w",
        "w",
        "w",
        "w",
        "w",
        "s",
        "s",
        "s",
        "e",
        "e",
        "e",
        "e",
        "e",
    ]  # second gift + house
    path += ["s", "s", "w", "w", "w", "w", "w"]  # third gift + house
    for step in path:
        game.move(step)
    assert game.is_won
    assert game.is_over
    assert "Victory" in game.status()


def test_serialization_round_trip_preserves_state():
    game = SantaGame()
    game.move("e")
    game.move("e")
    game.move("e")  # gift collected
    saved = game.to_dict()
    restored = SantaGame.from_dict(saved)
    assert restored.bag == game.bag
    assert restored.delivered == game.delivered
    assert restored.moves == game.moves
    assert restored.render() == game.render()


def test_board_cells_shapes_match_grid():
    game = SantaGame()
    cells = game.board_cells()
    assert len(cells) == len(game.grid)
    assert all(len(row) == len(game.grid[0]) for row in cells)
