from .abstract_solver_rule import SolverRule
from ...cell_change_info import CellChanges
from ...cell_state import CellState


class SeparateClues(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        A cell must be a wall if it is adjacent (non-diagonally) to more than one cell with a clue since gardens cannot
        have more than one clue.
        """
        cell_changes = CellChanges()
        for cell in self.board.get_empty_cells():
            if len([cell for adjacent_cell in cell.get_adjacent_neighbors() if adjacent_cell.has_clue]) > 1:
                cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL, reason='separate clues'))
        return cell_changes
