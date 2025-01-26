from line_profiler import profile
from dataclasses import dataclass

from ...board import Board
from ...cell import Cell
from ...cell_change_info import CellChanges, CellStateChange
from ...cell_state import CellState
from ...garden import Garden
from ..board_state_checker import BoardStateChecker, NoPossibleSolutionFromCurrentStateError
from ..path_finding import NoPathFoundError, PathFinder
from ..rule_trigger import ALL_POSSIBLE_CELL_STATE_CHANGES
from .abstract_solver_rule import SolverRule


@dataclass(frozen=True)
class PathToGardenInfo:
    garden: Garden
    path_cell_tuple: tuple[Cell, ...]


class EnsureGardenWithoutClueCanExpand(SolverRule):
    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return ALL_POSSIBLE_CELL_STATE_CHANGES

    @staticmethod
    def _get_rule_cost() -> float:
        return 54

    @staticmethod
    def _is_saturating_rule() -> bool:
        return False

    @profile
    def apply_rule(self) -> CellChanges:
        """
        If there is an incomplete garden without a clue and marking an empty cell as a wall would make it so that the
        garden would not be able to expand to reach a clue cell, that empty cell cannot be a wall, so mark it as a
        non-wall.
        """
        garden_info = GardenInfo(self.board)

        cell_changes = CellChanges()

        for garden_without_clue in garden_info.gardens_without_clue:
            # Get the set of gardens that are incomplete, have a clue, and are reachable from this garden_without_clue.
            # This also contains the shortest path to each garden.
            reachable_gardens_and_path = garden_info.get_reachable_gardens_and_path(
                source_garden_without_clue=garden_without_clue,
            )
            reachable_gardens = {
                reachable_garden_and_path.garden for reachable_garden_and_path in reachable_gardens_and_path
            }

            # If there are no reachable incomplete gardens with a clue, then this garden_without_clue breaks the rules
            # of a solved Nurikabe puzzle since it will be a garden without a clue.
            if len(reachable_gardens_and_path) == 0:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Garden without clue cannot reach a clue cell',
                    problem_cell_groups=frozenset({garden_without_clue}),
                )

            # Extract the set of empty cells that are in all the paths to reachable incomplete gardens with a clue.
            # These are the only possible cells that, if they were a wall, have the potential to block every path to the
            # aforementioned gardens.
            cells_in_all_paths: set[Cell] = set.intersection(
                *[
                    set(reachable_garden_and_path.path_cell_tuple)
                    for reachable_garden_and_path in reachable_gardens_and_path
                ],
            )
            empty_cells_in_all_paths = {cell for cell in cells_in_all_paths if cell.cell_state.is_empty()}

            # Each of the cells above has the *potential* to block every path to the aforementioned gardens. We'll need
            # to check each cell one-by-one. Set the order in which to check the cells. In a somewhat hand wavy way, we
            # think that cells closer to the garden_without_clue are more likely to be critical to all paths, so
            # prioritize based on distance to the garden_without_clue.
            prioritized_escape_route_cells = sorted(
                empty_cells_in_all_paths,
                key=lambda cell: garden_without_clue.get_shortest_manhattan_distance_to_cell(cell),
            )
            for escape_route_cell in prioritized_escape_route_cells:
                # TODO: also filter via flood fill?

                # If the escape_route_cell were to be marked as a wall, would any garden be reachable from the
                # garden_without_clue? If not, then the escape_route_cell cannot be a wall and is therefore marked as a
                # non-wall.
                is_any_garden_reachable = garden_info.is_any_garden_reachable(
                    source_garden_without_clue=garden_without_clue,
                    gardens_to_check=reachable_gardens,
                    additional_off_limit_cell=escape_route_cell,
                )
                if not is_any_garden_reachable:
                    cell_changes.add_change(
                        self.set_cell_to_state(
                            escape_route_cell,
                            CellState.NON_WALL,
                            reason='Ensure garden without clue can reach a clue cell',
                        )
                    )

                    # Since some cells were marked as non-walls, the previously calculated all_gardens is no longer
                    # valid
                    return cell_changes
        return cell_changes


class GardenInfo:
    def __init__(self, board: Board):
        self.board = board

        self.all_gardens = self.board.get_all_gardens()
        BoardStateChecker(self.board).check_for_garden_with_multiple_clues()

        self.gardens_with_clue = {garden for garden in self.all_gardens if garden.does_contain_clue()}
        self.gardens_without_clue = self.all_gardens - self.gardens_with_clue
        self.incomplete_gardens_with_clue = {
            garden for garden in self.gardens_with_clue if not garden.is_garden_correct_size()
        }
        self.incomplete_gardens = self.incomplete_gardens_with_clue.union(self.gardens_without_clue)
        self.complete_gardens = frozenset(self.all_gardens - self.incomplete_gardens)
        self.wall_cells = self.board.get_wall_cells()

    def get_reachable_gardens_and_path(
        self, source_garden_without_clue: Garden, additional_off_limit_cell: Cell | None = None
    ) -> set[PathToGardenInfo]:
        """
        Get a set of gardens (and the shortest path to that garden) that are reachable from source_garden_without_clue.
        """
        # Only bother checking gardens that are manhattan reachable
        manhattan_reachable_incomplete_gardens_with_clue = self.get_manhattan_reachable_incomplete_gardens_with_clue(
            source_garden_without_clue
        )

        # Only bother checking gardens that can be reached via a flood fill from source_garden_without_clue
        # TODO: Flood fill check may actually make it slower, so maybe exclude the flood fill filter?
        flood_fill_reachable_cells = self.get_flood_fill_reachable_cells(
            source_garden_without_clue,
            additional_off_limit_cell,
        )
        gardens_to_check = {
            garden
            for garden in manhattan_reachable_incomplete_gardens_with_clue
            if garden.does_include_cell(flood_fill_reachable_cells)
        }

        path_to_garden_info: set[PathToGardenInfo] = set()
        for destination_garden_with_clue in gardens_to_check:
            try:
                path_cell_list = self.get_path_to_incomplete_garden_with_clue(
                    source_garden_without_clue=source_garden_without_clue,
                    destination_garden_with_clue=destination_garden_with_clue,
                    additional_off_limit_cell=additional_off_limit_cell,
                )
                path_to_garden_info.add(
                    PathToGardenInfo(
                        garden=destination_garden_with_clue,
                        path_cell_tuple=tuple(path_cell_list),
                    )
                )
            except NoPathFoundError:
                pass
        return path_to_garden_info

    def get_flood_fill_reachable_cells(
        self, source_garden_without_clue: Garden, additional_off_limit_cell: Cell | None = None
    ) -> frozenset[Cell]:
        """
        Get the cells that can be accessed from the source_garden_without_clue without going through an off limit cell.
        Off limit cells are wall cells and any cell adjacent to a complete garden.
        """
        off_limit_cells = self.get_off_limit_cells(
            adjacent_off_limit_gardens=self.complete_gardens,
            additional_off_limit_cell=additional_off_limit_cell,
        )
        return self.board.get_connected_cells_with_cache(
            starting_cell=next(iter(source_garden_without_clue.cells)),
            valid_cells=frozenset(self.board.flat_cell_frozenset - off_limit_cells),
        )

    def get_manhattan_reachable_incomplete_gardens_with_clue(self, source_garden_without_clue: Garden) -> set[Garden]:
        return {
            garden
            for garden in self.incomplete_gardens_with_clue
            if GardenInfo.is_garden_manhattan_reachable(source_garden_without_clue, garden)
        }

    @staticmethod
    def is_garden_manhattan_reachable(source_garden_without_clue: Garden, incomplete_garden_with_clue: Garden) -> bool:
        # TODO: Add docstring
        manhattan_distance = incomplete_garden_with_clue.get_shortest_manhattan_distance_to_cell_group(
            source_garden_without_clue
        )
        remaining_garden_size = incomplete_garden_with_clue.get_num_of_remaining_garden_cells()
        source_garden_size = len(source_garden_without_clue.cells)

        # Compare to manhattan_distance - 1 since manhattan distance includes one end point whereas we want to know the
        # distance excluding both end points
        return manhattan_distance - 1 <= remaining_garden_size - source_garden_size

    def is_any_garden_reachable(
        self,
        source_garden_without_clue: Garden,
        gardens_to_check: set[Garden],
        additional_off_limit_cell: Cell | None = None,
    ) -> bool:
        """Check if any of the gardens in gardens_to_check reachable from source_garden_without_clue."""
        for destination_garden_with_clue in gardens_to_check:
            try:
                self.get_path_to_incomplete_garden_with_clue(
                    source_garden_without_clue=source_garden_without_clue,
                    destination_garden_with_clue=destination_garden_with_clue,
                    additional_off_limit_cell=additional_off_limit_cell,
                )
            except NoPathFoundError:
                pass
            else:
                return True
        return False

    def get_path_to_incomplete_garden_with_clue(
        self,
        source_garden_without_clue: Garden,
        destination_garden_with_clue: Garden,
        additional_off_limit_cell: Cell | None = None,
    ) -> list[Cell]:
        """Find the (shortest) path from the source_garden_without_clue to the destination_garden_with_clue."""
        other_gardens_without_clue = self.gardens_without_clue - {source_garden_without_clue}
        other_gardens_with_clue = frozenset(self.gardens_with_clue - {destination_garden_with_clue})
        off_limit_cells = self.get_off_limit_cells(
            adjacent_off_limit_gardens=other_gardens_with_clue,
            additional_off_limit_cell=additional_off_limit_cell,
        )
        path_finder = PathFinder(
            start_cell_group=source_garden_without_clue,
            end_cell_group=destination_garden_with_clue,
            off_limit_cells=off_limit_cells,
            other_cell_groups=frozenset(other_gardens_without_clue),
        )
        max_total_path_length = destination_garden_with_clue.get_clue_value()
        remaining_available_cells = (
            max_total_path_length - len(source_garden_without_clue.cells) - len(destination_garden_with_clue.cells)
        )

        # Add two since the path length includes both the starting and ending cell
        remaining_available_path_length = remaining_available_cells + 2
        path_info = path_finder.get_path_info(max_path_length=remaining_available_path_length)
        return path_info.cell_list

    def get_off_limit_cells(
        self, adjacent_off_limit_gardens: frozenset[Garden], additional_off_limit_cell: Cell | None = None
    ) -> frozenset[Cell]:
        off_limit_cells: set[Cell] = set()
        off_limit_cells.update(self.wall_cells)

        for garden in adjacent_off_limit_gardens:
            off_limit_cells.update(garden.get_adjacent_neighbors())

        if additional_off_limit_cell is not None:
            off_limit_cells.add(additional_off_limit_cell)

        return frozenset(off_limit_cells)
