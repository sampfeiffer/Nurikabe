from enum import Enum, auto
from dataclasses import dataclass


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()
    RIGHT_UP = auto()
    LEFT_UP = auto()
    RIGHT_DOWN = auto()
    LEFT_DOWN = auto()


ADJACENT_DIRECTIONS = (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT)


@dataclass
class GridOffset:
    row_offset: int
    col_offset: int


OFFSET_MAP = {
    Direction.UP: GridOffset(row_offset=-1, col_offset=0),
    Direction.DOWN: GridOffset(row_offset=1, col_offset=0),
    Direction.RIGHT: GridOffset(row_offset=0, col_offset=1),
    Direction.LEFT: GridOffset(row_offset=0, col_offset=-1),
    Direction.RIGHT_UP: GridOffset(row_offset=-1, col_offset=1),
    Direction.LEFT_UP: GridOffset(row_offset=-1, col_offset=-1),
    Direction.RIGHT_DOWN: GridOffset(row_offset=1, col_offset=1),
    Direction.LEFT_DOWN: GridOffset(row_offset=1, col_offset=-1)
}
