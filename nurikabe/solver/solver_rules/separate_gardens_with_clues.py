from collections import Counter

from ...cell_change_info import CellChanges
from ...cell_state import CellState
from .abstract_solver_rule import SolverRule


class SeparateGardensWithClues(SolverRule):
    def apply_rule(self) -> CellChanges:
        """If an empty cell is adjacent to more than one garden containing a clue, then it must be a wall."""
        cell_changes = CellChanges()
        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        empty_neighbor_sets = {
            incomplete_garden.get_empty_adjacent_neighbors() for incomplete_garden in incomplete_gardens
        }
        all_empty_neighbor_cells = [cell for adjacent_cells in empty_neighbor_sets for cell in adjacent_cells]
        cell_counts = Counter(all_empty_neighbor_cells)
        cells_neighboring_multiple_gardens = {cell for cell, count in cell_counts.items() if count > 1}
        for cell in cells_neighboring_multiple_gardens:
            cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL, reason='Adjacent to multiple gardens'))
        return cell_changes
