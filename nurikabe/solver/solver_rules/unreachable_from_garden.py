from .abstract_solver_rule import SolverRule
from ..board_state_checker import NoPossibleSolutionFromCurrentState
from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ...cell import Cell
from ...garden import Garden
from ..path_finding import find_shortest_path_cell_group_to_cell, NoPathFoundError


class UnreachableFromGarden(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        If there are any empty cells that are unreachable by a garden, it must be a wall. For any incomplete garden
        with a clue, this detects the reachable cells. If there are empty cells that are not reachable by all gardens
        with clues, then those empty cells must be walls.
        """
        cell_changes = CellChanges()
        all_gardens = self.board.get_all_gardens()
        gardens_with_clue = {garden for garden in all_gardens if garden.does_contain_clue()}
        incomplete_gardens_with_clue = {garden for garden in gardens_with_clue if not garden.is_garden_correct_size()}
        gardens_without_clue = all_gardens - gardens_with_clue
        all_reachable_cells: set[Cell] = set()
        for incomplete_garden_with_clue in incomplete_gardens_with_clue:
            other_gardens_with_clues = gardens_with_clue - {incomplete_garden_with_clue}
            reachable_from_garden = self.get_cells_reachable_from_garden(
                source_garden=incomplete_garden_with_clue,
                other_gardens_with_clues=other_gardens_with_clues,
                gardens_without_clue=gardens_without_clue
            )
            all_reachable_cells = all_reachable_cells.union(reachable_from_garden)
        for cell in self.board.get_empty_cells():
            if cell not in all_reachable_cells:
                cell_changes.add_change(
                    self.set_cell_to_state(cell, CellState.WALL,
                                           reason='Not reachable by any incomplete gardens with clues')
                )
                # TODO - should this return right away?
        return cell_changes

    def get_cells_reachable_from_garden(self, source_garden: Garden, other_gardens_with_clues: set[Garden],
                                        gardens_without_clue: set[Garden]) -> set[Cell]:
        if not source_garden.does_have_exactly_one_clue():
            raise NoPossibleSolutionFromCurrentState(
                message='Cannot determine reach of garden since there is not exactly one clue',
                problem_cell_groups={source_garden}
            )

        # Determine which cells are not able to be a part of the source_garden
        off_limits_cells = self.board.get_wall_cells()
        for garden in other_gardens_with_clues:
            off_limits_cells = off_limits_cells.union(garden.cells)
            off_limits_cells = off_limits_cells.union(garden.get_adjacent_neighbors())

        # Get the cells that can be accessed from source_garden without going through a cell in off_limits_cells
        potentially_reachable_cells = self.board.get_connected_cells(
            starting_cell=source_garden.get_clue_cell(),
            cell_criteria_func=lambda x: x not in off_limits_cells
        )

        # From among the potentially reachable cells, extract the set of cells for which we want to check for
        # reachability.
        num_of_remaining_garden_cells = source_garden.get_num_of_remaining_garden_cells()
        target_cells = potentially_reachable_cells.intersection(self.board.get_empty_cells())

        # Check each target cell to determine if it is reachable
        reachable_cells: set[Cell] = set()
        for target_cell in target_cells:
            try:
                find_shortest_path_cell_group_to_cell(
                    start_cell_group=source_garden,
                    end_cell=target_cell,
                    off_limits_cells=off_limits_cells,
                    max_path_length=num_of_remaining_garden_cells + 1,
                    other_cell_groups=gardens_without_clue
                )
                reachable_cells.add(target_cell)
            except NoPathFoundError:
                # target_cell is not reachable from the source_garden
                pass

        return reachable_cells
