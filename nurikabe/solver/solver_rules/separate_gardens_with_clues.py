from line_profiler import profile
from collections import Counter

from ...cell_change_info import CellChanges, CellStateChange
from ...cell_state import CellState
from ..board_state_checker import BoardStateChecker
from ..rule_trigger import RuleTrigger
from .abstract_solver_rule import SolverRule


class SeparateGardensWithClues(SolverRule):
    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return frozenset({
            RuleTrigger.WALL_TO_NON_WALL.value,
            RuleTrigger.WALL_TO_EMPTY.value,
            RuleTrigger.NON_WALL_TO_WALL.value,
            RuleTrigger.NON_WALL_TO_EMPTY.value,
            RuleTrigger.EMPTY_TO_NON_WALL.value,
        })

    @staticmethod
    def _get_rule_cost() -> float:
        return 48

    @staticmethod
    def _is_saturating_rule() -> bool:
        return True

    @profile
    def apply_rule(self) -> CellChanges:
        """If an empty cell is adjacent to more than one garden containing a clue, then it must be a wall."""
        BoardStateChecker(self.board).check_for_garden_with_multiple_clues()

        cell_changes = CellChanges()

        all_gardens = self.board.get_all_gardens()
        gardens_with_clue = frozenset({garden for garden in all_gardens if garden.does_contain_clue()})
        empty_neighbor_sets = {garden.get_empty_adjacent_neighbors() for garden in gardens_with_clue}
        all_empty_neighbor_cells = [cell for adjacent_cells in empty_neighbor_sets for cell in adjacent_cells]
        cell_counts = Counter(all_empty_neighbor_cells)
        cells_neighboring_multiple_gardens = {cell for cell, count in cell_counts.items() if count > 1}
        for cell in cells_neighboring_multiple_gardens:
            cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL, reason='Adjacent to multiple gardens'))
        return cell_changes
