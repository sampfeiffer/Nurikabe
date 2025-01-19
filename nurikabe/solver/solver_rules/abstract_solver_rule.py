import logging
from abc import ABC, abstractmethod

from ...board import Board
from ...cell import Cell
from ...cell_change_info import CellChangeInfo, CellChanges
from ...cell_state import CellState
from ...garden import Garden

logger = logging.getLogger(__name__)


class SolverRule(ABC):
    def __init__(self, board: Board):
        self.board = board

    @abstractmethod
    def apply_rule(self) -> CellChanges:
        raise NotImplementedError

    def set_cell_to_state(self, cell: Cell, target_cell_state: CellState, reason: str) -> CellChangeInfo:
        if not cell.is_clickable:
            msg = f'cell is not clickable: {cell}'
            raise RuntimeError(msg)
        logger.debug('Setting %s to %s. Reason: %s', cell, target_cell_state, reason)
        cell_change_info = cell.update_cell_state(target_cell_state)
        self.board.reset_cell_state_hash()
        return cell_change_info

    def get_incomplete_gardens(self, *, with_clue_only: bool) -> set[Garden]:
        all_gardens = self.board.get_all_gardens()
        incomplete_gardens = {
            garden for garden in all_gardens if not garden.does_contain_clue() or not garden.is_garden_correct_size()
        }
        if with_clue_only:
            incomplete_gardens = {garden for garden in incomplete_gardens if garden.does_contain_clue()}
        return incomplete_gardens
