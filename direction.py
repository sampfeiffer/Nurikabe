from enum import Enum, auto


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


OFFSET_MAP = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.RIGHT: (1, 0),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT_UP: (1, -1),
    Direction.LEFT_UP: (-1, -1),
    Direction.RIGHT_DOWN: (1, 1),
    Direction.LEFT_DOWN: (-1, 1)
}
