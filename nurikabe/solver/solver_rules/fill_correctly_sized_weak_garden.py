from ...cell_change_info import CellChanges
from ...cell_state import CellState
from .abstract_solver_rule import SolverRule


class FillCorrectlySizedWeakGarden(SolverRule):
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
                    cell_changes.add_change(self.set_cell_to_state(cell, CellState.NON_WALL,
                                                                   reason='Fill completed weak garden'))
        return cell_changes
