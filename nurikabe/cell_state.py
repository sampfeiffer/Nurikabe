from __future__ import annotations

from collections.abc import Callable
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
            cell_state = CellState.WALL
        elif self is CellState.WALL:
            cell_state = CellState.NON_WALL
        elif self is CellState.NON_WALL:
            cell_state = CellState.EMPTY
        elif self is CellState.CLUE:
            msg = 'clue cells are not clickable'
            raise RuntimeError(msg)
        else:
            msg = 'This should not be possible'
            raise RuntimeError(msg)
        return cell_state

    @staticmethod
    def is_empty_static(cell_state: CellState) -> bool:
        return cell_state.is_empty()

    @staticmethod
    def is_wall_static(cell_state: CellState) -> bool:
        return cell_state.is_wall()

    @staticmethod
    def is_clue_static(cell_state: CellState) -> bool:
        return cell_state.is_clue()

    @staticmethod
    def is_garden_static(cell_state: CellState) -> bool:
        return cell_state.is_garden()

    @staticmethod
    def is_weak_garden_static(cell_state: CellState) -> bool:
        return cell_state.is_weak_garden()


CellStateCriteriaFunc = Callable[[CellState], bool]
