from ...cell import Cell
from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ...garden import Garden
from ..board_state_checker import NoPossibleSolutionFromCurrentStateError
from ..path_finding import NoPathFoundError, PathFinder
from .abstract_solver_rule import SolverRule


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
                gardens_without_clue=gardens_without_clue,
            )
            all_reachable_cells = all_reachable_cells.union(reachable_from_garden)
        for cell in self.board.get_empty_cells():
            if cell not in all_reachable_cells:
                cell_changes.add_change(
                    self.set_cell_to_state(
                        cell,
                        CellState.WALL,
                        reason='Not reachable by any incomplete gardens with clues',
                    ),
                )
                # TODO: should this return right away?
        return cell_changes

    def get_cells_reachable_from_garden(
        self, source_garden: Garden, other_gardens_with_clues: set[Garden], gardens_without_clue: set[Garden]
    ) -> set[Cell]:
        if not source_garden.does_have_exactly_one_clue():
            raise NoPossibleSolutionFromCurrentStateError(
                message='Cannot determine reach of garden since there is not exactly one clue',
                problem_cell_groups=frozenset({source_garden}),
            )

        # Determine which cells are not able to be a part of the source_garden
        off_limit_cells = self.board.get_wall_cells()
        for garden in other_gardens_with_clues:
            off_limit_cells = off_limit_cells.union(garden.cells)
            off_limit_cells = off_limit_cells.union(garden.get_adjacent_neighbors())

        # Get the cells that can be accessed from source_garden without going through a cell in off_limit_cells
        potentially_reachable_cells = self.board.get_connected_cells(
            starting_cell=source_garden.get_clue_cell(),
            cell_criteria_func=lambda x: x not in off_limit_cells,
        )

        # From among the potentially reachable cells, extract the set of cells for which we want to check for
        # reachability.
        num_of_remaining_garden_cells = source_garden.get_num_of_remaining_garden_cells()
        target_cells = potentially_reachable_cells.intersection(self.board.get_empty_cells())

        # Check each target cell to determine if it is reachable
        reachable_cells: set[Cell] = set()
        for target_cell in target_cells:
            try:
                PathFinder(
                    start_cell_group=source_garden,
                    end_cell_group=target_cell,
                    off_limit_cells=off_limit_cells,
                    other_cell_groups=frozenset(gardens_without_clue),
                ).get_path_info(max_path_length=num_of_remaining_garden_cells + 1)
                reachable_cells.add(target_cell)
            except NoPathFoundError:
                # target_cell is not reachable from the source_garden
                pass

        return reachable_cells
