from __future__ import annotations
from enum import Enum, auto


class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    NON_WALL = auto()
    CLUE = auto()

    def is_empty(self) -> bool:
        return self is CellState.EMPTY

    def is_wall(self) -> bool:
        return self is CellState.WALL

    def is_non_wall(self) -> bool:
        return self is CellState.NON_WALL

    def is_clue(self) -> bool:
        return self is CellState.CLUE

    def is_garden(self) -> bool:
        return self.is_non_wall() or self.is_clue()

    def is_weak_garden(self) -> bool:
        return self.is_garden() or self.is_empty()

    def get_next_in_cycle(self) -> CellState:
        """When the user clicks on a cell, it cycles through these states."""
        if self is CellState.EMPTY:
            return CellState.WALL
        elif self is CellState.WALL:
            return CellState.NON_WALL
        elif self is CellState.NON_WALL:
            return CellState.EMPTY
        elif self is CellState.CLUE:
            raise RuntimeError('clue cells are not clickable')
        else:
            raise RuntimeError('This should not be possible')
