import logging
from abc import ABC, abstractmethod

from ...board import Board
from ...cell import Cell
from ...cell_change_info import CellChangeInfo, CellChanges, CellStateChange
from ...cell_state import CellState
from ...garden import Garden

logger = logging.getLogger(__name__)


class SolverRule(ABC):
    def __init__(self, board: Board):
        self.board = board
        self.rule_triggers = self._get_rule_triggers()
        self.rule_cost = self._get_rule_cost()
        self.is_saturating_rule = self._is_saturating_rule()

    @staticmethod
    @abstractmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _get_rule_cost() -> float:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _is_saturating_rule() -> bool:
        raise NotImplementedError

    def should_trigger_rule(self, unique_cell_state_changes: frozenset[CellStateChange]) -> bool:
        return len(unique_cell_state_changes.intersection(self.rule_triggers)) > 0

    @abstractmethod
    def apply_rule(self) -> CellChanges:
        raise NotImplementedError

    def set_cell_to_state(self, cell: Cell, target_cell_state: CellState, reason: str) -> CellChangeInfo:
        if not cell.is_clickable:
            msg = f'cell is not clickable: {cell}'
            raise RuntimeError(msg)
        logger.info('Setting %s to %s. Reason: %s', cell, target_cell_state, reason)
        cell_change_info = cell.update_cell_state(target_cell_state, reason=reason)
        self.board.reset_cell_state_hash()
        return cell_change_info

    def get_incomplete_gardens(self, *, with_clue_only: bool) -> frozenset[Garden]:
        all_gardens = self.board.get_all_gardens()
        incomplete_gardens = {
            garden for garden in all_gardens if not garden.does_contain_clue() or not garden.is_garden_correct_size()
        }
        if with_clue_only:
            incomplete_gardens = {garden for garden in incomplete_gardens if garden.does_contain_clue()}
        return frozenset(incomplete_gardens)
