from line_profiler import profile
from ...cell_change_info import CellChanges, CellStateChange
from ...cell_state import CellState
from ..rule_trigger import RuleTrigger
from .abstract_solver_rule import SolverRule


class FillCorrectlySizedWeakGarden(SolverRule):
    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return frozenset({
            RuleTrigger.WALL_TO_NON_WALL.value,
            RuleTrigger.WALL_TO_EMPTY.value,
            RuleTrigger.NON_WALL_TO_WALL.value,
            RuleTrigger.NON_WALL_TO_EMPTY.value,
            RuleTrigger.EMPTY_TO_WALL.value,
        })

    @staticmethod
    def _get_rule_cost() -> float:
        return 50

    @staticmethod
    def _is_saturating_rule() -> bool:
        return True

    @profile
    def apply_rule(self) -> CellChanges:
        """
        If there is a weak garden that is the correct size but has some empty cells, mark the empty cells as non-walls.
        """
        cell_changes = CellChanges()
        all_weak_gardens = self.board.get_all_weak_gardens()
        for weak_garden in all_weak_gardens:
            if weak_garden.does_have_exactly_one_clue() and weak_garden.is_garden_correct_size():
                empty_cells = {cell for cell in weak_garden.cells if cell.cell_state.is_empty()}
                for cell in empty_cells:
                    cell_changes.add_change(
                        self.set_cell_to_state(cell, CellState.NON_WALL, reason='Fill completed weak garden')
                    )
        return cell_changes
