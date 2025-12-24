"""Core logic for the Santa delivery mini game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

Coordinate = Tuple[int, int]

# fmt: off
GRID_TEMPLATE = [
    "#########",
    "#S..G..H#",
    "#...#...#",
    "#..#....#",
    "#G....H.#",
    "#...#...#",
    "#H..G...#",
    "#########",
]
# fmt: on

DELTAS: Dict[str, Coordinate] = {
    "n": (-1, 0),
    "s": (1, 0),
    "w": (0, -1),
    "e": (0, 1),
}


@dataclass
class SantaGame:
    """Stateful model that tracks the progress of the Santa delivery game."""

    max_moves: int = 28
    grid: List[List[str]] = field(
        default_factory=lambda: [list(row) for row in GRID_TEMPLATE]
    )
    santa_pos: Optional[Coordinate] = None
    bag: int = 0
    delivered: int = 0
    moves: int = 0
    history: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.grid else 0
        self.santa_pos = self._find_first("S")
        if self.santa_pos is None:
            raise ValueError("Santa start position 'S' is required on the grid.")
        self.gifts: Set[Coordinate] = set(self._find_all("G"))
        self.houses: Set[Coordinate] = set(self._find_all("H"))
        self._wins_at = len(self.gifts)

    def _find_first(self, marker: str) -> Optional[Coordinate]:
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == marker:
                    return (r, c)
        return None

    def _find_all(self, marker: str) -> Iterable[Coordinate]:
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == marker:
                    yield (r, c)

    def render(self) -> str:
        """Return a printable version of the current map."""
        lines = []
        for r, row in enumerate(self.grid):
            rendered_row = []
            for c, cell in enumerate(row):
                if (r, c) == self.santa_pos:
                    rendered_row.append("S")
                elif (r, c) in self.gifts:
                    rendered_row.append("G")
                elif (r, c) in self.houses:
                    rendered_row.append("H")
                elif cell == "#":
                    rendered_row.append("#")
                else:
                    rendered_row.append(".")
            lines.append("".join(rendered_row))
        return "\n".join(lines)

    def _target_cell(self, direction: str) -> Coordinate:
        dr, dc = DELTAS[direction]
        sr, sc = self.santa_pos  # type: ignore[misc]
        return sr + dr, sc + dc

    def move(self, direction: str) -> str:
        """Move Santa in the specified direction if possible."""
        direction = direction.lower()
        if direction not in DELTAS:
            message = "Unknown direction. Use N, S, E, or W."
            self.history.append(message)
            return message

        target = self._target_cell(direction)
        if not self._is_walkable(target):
            options = ", ".join(m.upper() for m in self.available_moves())
            message = (
                f"A snowbank blocks the path! "
                f"{'Try: ' + options if options else 'No paths open.'}"
            )
            self.history.append(message)
            return message

        self.santa_pos = target
        self.moves += 1

        gift_msg = self._collect_gift_if_present()
        delivery_msg = self._deliver_if_possible()

        summary = f"Moved {direction.upper()}."
        if gift_msg:
            summary = f"{summary} {gift_msg}"
        if delivery_msg:
            summary = f"{summary} {delivery_msg}"

        self.history.append(summary)
        return summary

    def _is_walkable(self, coord: Coordinate) -> bool:
        r, c = coord
        if r < 0 or c < 0 or r >= self.height or c >= self.width:
            return False
        return self.grid[r][c] != "#"

    def _collect_gift_if_present(self) -> str:
        if self.santa_pos in self.gifts:
            self.gifts.remove(self.santa_pos)  # type: ignore[arg-type]
            self.bag += 1
            return "Picked up a gift."
        return ""

    def _deliver_if_possible(self) -> str:
        if self.santa_pos in self.houses and self.bag > 0:
            delivered_now = self.bag
            self.delivered += delivered_now
            self.bag = 0
            return f"Delivered {delivered_now} gift(s)!"
        return ""

    @property
    def remaining_moves(self) -> int:
        return max(self.max_moves - self.moves, 0)

    @property
    def is_won(self) -> bool:
        return not self.gifts and self.bag == 0

    @property
    def is_lost(self) -> bool:
        return self.moves >= self.max_moves and not self.is_won

    @property
    def is_over(self) -> bool:
        return self.is_won or self.is_lost

    def available_moves(self) -> List[str]:
        """Return list of directions that are walkable from current position."""
        options = []
        for d, delta in DELTAS.items():
            if self._is_walkable(self._target_cell(d)):
                options.append(d)
        return options

    def status(self) -> str:
        if self.is_won:
            return "Victory! Every house received a gift. 🎄"
        if self.is_lost:
            return "The night ended before Santa finished deliveries."
        return (
            f"Bag: {self.bag} | Delivered: {self.delivered}/{self._wins_at} | "
            f"Moves left: {self.remaining_moves} | "
            f"Open paths: {', '.join(m.upper() for m in self.available_moves()) or 'None'}"
        )

    def to_dict(self) -> Dict:
        """Serialize the game for storage."""
        return {
            "max_moves": self.max_moves,
            "grid": ["".join(row) for row in self.grid],
            "santa_pos": list(self.santa_pos) if self.santa_pos is not None else None,
            "bag": self.bag,
            "delivered": self.delivered,
            "moves": self.moves,
            "history": list(self.history),
            "gifts": [list(g) for g in self.gifts],
            "houses": [list(h) for h in self.houses],
            "_wins_at": self._wins_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SantaGame":
        """Rehydrate a game from serialized data."""
        grid_rows = [list(row) for row in data["grid"]]
        game = cls(max_moves=data["max_moves"], grid=grid_rows)
        game.santa_pos = tuple(data["santa_pos"]) if data["santa_pos"] else None
        game.bag = data["bag"]
        game.delivered = data["delivered"]
        game.moves = data["moves"]
        game.history = list(data["history"])
        game.gifts = {tuple(g) for g in data["gifts"]}
        game.houses = {tuple(h) for h in data["houses"]}
        game._wins_at = data.get("_wins_at", len(game.gifts))
        return game

    def board_cells(self) -> List[List[str]]:
        """Return a grid of cell types for UI rendering."""
        cells: List[List[str]] = []
        for r, row in enumerate(self.grid):
            rendered_row: List[str] = []
            for c, cell in enumerate(row):
                coord = (r, c)
                if coord == self.santa_pos:
                    rendered_row.append("santa")
                elif coord in self.gifts:
                    rendered_row.append("gift")
                elif coord in self.houses:
                    rendered_row.append("house")
                elif cell == "#":
                    rendered_row.append("wall")
                else:
                    rendered_row.append("path")
            cells.append(rendered_row)
        return cells

    @staticmethod
    def help_text() -> str:
        return (
            "Commands: N, S, E, W to move. LOOK to view the map, STATUS for progress, "
            "and QUIT to exit."
        )
