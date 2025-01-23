from ...cell_change_info import CellChanges
from ...cell_state import CellState
from .abstract_solver_rule import SolverRule


class SeparateClues(SolverRule):
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
                cell_changes.add_change(self.set_cell_to_state(empty_cell, CellState.WALL, reason='separate clues'))
        return cell_changes
