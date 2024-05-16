from ...cell import Cell
from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ...garden import Garden
from ..board_state_checker import BoardStateChecker, NoPossibleSolutionFromCurrentStateError
from .abstract_solver_rule import SolverRule


class EnsureGardenWithClueCanExpand(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        If there is an incomplete garden with a clue and marking an empty cell as a wall would make it so that the
        garden would not be able to expand the required size, that empty cell cannot be a wall, so mark it as a
        non-wall.
        """
        BoardStateChecker(self.board).check_for_garden_with_multiple_clues()

        all_gardens = self.board.get_all_gardens()
        gardens_with_clue = {garden for garden in all_gardens if garden.does_contain_clue()}
        incomplete_gardens_with_clue = {garden for garden in gardens_with_clue if not garden.is_garden_correct_size()}

        cell_changes = CellChanges()

        for incomplete_garden_with_clue in incomplete_gardens_with_clue:
            off_limit_cells = self.get_off_limit_cells(
                gardens_with_clue=gardens_with_clue,
                this_garden=incomplete_garden_with_clue,
            )

            # Get the set of cells that can be reached via a flood fill from the clue cell while avoiding off limit
            # cells
            clue_cell = incomplete_garden_with_clue.get_clue_cell()
            clue_value = clue_cell.get_non_null_clue()
            potentially_reachable_cells_from_garden = self.board.get_connected_cells(
                starting_cell=clue_cell,
                cell_criteria_func=lambda cell: cell not in off_limit_cells,  # noqa: B023
            )

            # If the number of potentially reachable cells is fewer than the clue value, then the garden does not have
            # enough space to expand and the board is in a bad state, so throw an error
            if len(potentially_reachable_cells_from_garden) < clue_value:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Incomplete garden with clue cannot expand to appropriate size',
                    problem_cell_groups={incomplete_garden_with_clue},
                )

            # Farther filter down the potentially_reachable_cells_from_garden to only include cells that we need to
            # for its "blocking" capability.
            escape_route_cells = potentially_reachable_cells_from_garden - incomplete_garden_with_clue.cells
            escape_route_cells = {cell for cell in escape_route_cells if cell.cell_state.is_empty()}

            # Additionally, filter to only include cells that are Manhattan reachable from the
            # incomplete_garden_with_clue
            remaining_garden_size = incomplete_garden_with_clue.get_num_of_remaining_garden_cells()
            escape_route_cells = {
                cell for cell in escape_route_cells if
                incomplete_garden_with_clue.get_shortest_manhattan_distance_to_cell(cell) <= remaining_garden_size
            }

            prioritized_escape_route_cells = self.get_prioritized_escape_route_cells(
                escape_route_cells=escape_route_cells,
                source_garden=incomplete_garden_with_clue,
            )

            for escape_route_cell in prioritized_escape_route_cells:
                # If the escape_route_cell were to be marked as a wall, would the incomplete_garden_with_clue be able to
                # expand to the appropriate size? If not, then the escape_route_cell cannot be a wall and is therefore
                # marked as a non-wall.
                off_limit_cells_for_this_escape_route = off_limit_cells.union({escape_route_cell})
                potentially_reachable_cells = self.board.get_connected_cells(
                    starting_cell=clue_cell,
                    cell_criteria_func=lambda x: x not in off_limit_cells_for_this_escape_route,  # noqa: B023
                )
                if len(potentially_reachable_cells) < clue_value:
                    cell_changes.add_change(self.set_cell_to_state(
                        escape_route_cell,
                        CellState.NON_WALL,
                        reason='Ensure garden with clue can expand',
                    ))

                    # Since some cells were marked as non-walls, the previously calculated all_gardens is no longer
                    # valid
                    return cell_changes

        return cell_changes

    @staticmethod
    def get_prioritized_escape_route_cells(escape_route_cells: set[Cell], source_garden: Garden) -> list[Cell]:
        """
        Set the order in which to check the escape route cells. In a somewhat hand wavy way, we think that cells
        closer to the source_garden are more likely to be critical, so prioritize based on distance to the
        source_garden.
        """
        return sorted(escape_route_cells, key=lambda cell: source_garden.get_shortest_manhattan_distance_to_cell(cell))

    def get_off_limit_cells(self, gardens_with_clue: set[Garden], this_garden: Garden) -> set[Cell]:
        off_limit_cells: set[Cell] = set()
        off_limit_cells.update(self.board.get_wall_cells())

        other_gardens_with_clue = gardens_with_clue - {this_garden}
        for garden in other_gardens_with_clue:
            off_limit_cells.update(garden.get_adjacent_neighbors())

        return off_limit_cells
