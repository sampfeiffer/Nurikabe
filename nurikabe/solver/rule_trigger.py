from enum import Enum

from ..cell_change_info import CellStateChange
from ..cell_state import CellState


class RuleTrigger(Enum):
    WALL_TO_NON_WALL = CellStateChange(CellState.WALL, CellState.NON_WALL)
    WALL_TO_EMPTY = CellStateChange(CellState.WALL, CellState.EMPTY)
    NON_WALL_TO_WALL = CellStateChange(CellState.NON_WALL, CellState.WALL)
    NON_WALL_TO_EMPTY = CellStateChange(CellState.NON_WALL, CellState.EMPTY)
    EMPTY_TO_WALL = CellStateChange(CellState.EMPTY, CellState.WALL)
    EMPTY_TO_NON_WALL = CellStateChange(CellState.EMPTY, CellState.NON_WALL)

ALL_POSSIBLE_CELL_STATE_CHANGES = frozenset({rule_trigger.value for rule_trigger in RuleTrigger})
