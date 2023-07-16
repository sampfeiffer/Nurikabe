from enum import Enum, auto


class TextType(Enum):
    CELL = auto()
    PUZZLE_SOLVED = auto()
    BUTTON = auto()
    GRID_NUMBERING = auto()
