from ...cell_change_info import CellChanges
from ...cell_state import CellState
from .abstract_solver_rule import SolverRule


class NaivelyUnreachableFromGarden(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        If there are any empty cells that are naively unreachable by a garden, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be
        allowed. This checks if cells are reachable from a garden in the remaining number of missing non-wall cells
        for that garden.
        """
        cell_changes = CellChanges()
        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        incomplete_gardens_and_remaining_sizes = [
            (incomplete_garden, incomplete_garden.get_num_of_remaining_garden_cells())
            for incomplete_garden in incomplete_gardens
        ]

        for cell in self.board.get_empty_cells():
            is_cell_reachable_by_a_clue = False
            for incomplete_garden, remaining_garden_size in incomplete_gardens_and_remaining_sizes:
                if incomplete_garden.get_shortest_manhattan_distance_to_cell(cell) <= remaining_garden_size:
                    is_cell_reachable_by_a_clue = True
                    break
            if not is_cell_reachable_by_a_clue:
                cell_changes.add_change(
                    self.set_cell_to_state(cell, CellState.WALL, reason='Not Manhattan reachable by any gardens')
                )
        return cell_changes
