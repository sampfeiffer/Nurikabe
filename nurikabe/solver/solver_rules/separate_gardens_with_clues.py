from typing import TYPE_CHECKING

from ...cell_change_info import CellChanges
from ...cell_state import CellState
from .abstract_solver_rule import SolverRule

if TYPE_CHECKING:
    from ...cell import Cell


class SeparateGardensWithClues(SolverRule):
    def apply_rule(self) -> CellChanges:
        """If a cell is adjacent to more than one garden containing a clue, than it must be a wall."""
        cell_changes = CellChanges()
        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        all_empty_adjacent_cells: set[Cell] = set()
        for incomplete_garden in incomplete_gardens:
            empty_adjacent_cells = incomplete_garden.get_empty_adjacent_neighbors()
            for cell in empty_adjacent_cells:
                if cell in all_empty_adjacent_cells:
                    cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                                   reason='Adjacent to multiple gardens'))
                all_empty_adjacent_cells.add(cell)
        return cell_changes
