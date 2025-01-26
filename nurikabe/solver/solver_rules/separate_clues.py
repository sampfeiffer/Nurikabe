from line_profiler import profile
from ...cell_change_info import CellChanges, CellStateChange
from ...cell_state import CellState
from ..rule_trigger import RuleTrigger
from .abstract_solver_rule import SolverRule


class SeparateClues(SolverRule):
    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return frozenset({RuleTrigger.WALL_TO_EMPTY.value, RuleTrigger.NON_WALL_TO_EMPTY.value})

    @staticmethod
    def _get_rule_cost() -> float:
        return 13

    @staticmethod
    def _is_saturating_rule() -> bool:
        return True

    @profile
    def apply_rule(self) -> CellChanges:
        """
        A cell must be a wall if it is adjacent (non-diagonally) to more than one cell with a clue since gardens cannot
        have more than one clue.
        """
        cell_changes = CellChanges()
        for empty_cell in self.board.get_empty_cells():
            neighbors_with_clue = [
                adjacent_cell for adjacent_cell in empty_cell.get_adjacent_neighbors() if adjacent_cell.has_clue
            ]
            if len(neighbors_with_clue) > 1:
                cell_changes.add_change(self.set_cell_to_state(empty_cell, CellState.WALL, reason='Separate clues'))
        return cell_changes
