from __future__ import annotations
from enum import Enum, auto


class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    NON_WALL = auto()

    def get_next_in_cycle(self) -> CellState:
        if self is CellState.EMPTY:
            return CellState.WALL
        elif self is CellState.WALL:
            return CellState.NON_WALL
        elif self is CellState.NON_WALL:
            return CellState.EMPTY
        else:
            raise RuntimeError('This should not be possible')
