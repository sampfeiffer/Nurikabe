import math
import queue
from dataclasses import dataclass, field

from ..cell import Cell
from ..cell_group import CellGroup
from .path_info import PathInfo


class NoPathFoundError(Exception):
    """Indicates that no path could be found within the given constraints."""


class PathSetupError(Exception):
    """Indicates that there was something wrong with how the path finding problem was defined."""


@dataclass(order=True)
class PrioritizedCell:
    """Used in the A* path finding algorithm to determine the next cell to investigate."""

    priority: int
    cell: Cell = field(compare=False)


class PathFinder:
    """
    Uses A* algorithm to find the shortest path between two cell groups. The wiki page has a great explanation of the
    basic A* algorithm: https://en.wikipedia.org/wiki/A*_search_algorithm .

    The heuristic get_shortest_naive_path_length_to_cell_group is admissible meaning that this length is never greater
    than the actual shortest path length. The heuristic is also consistent since when going from two neighboring cells,
    the change in heuristic never over-estimates the actual cost of the step.
    """

    def __init__(
        self,
        start_cell_group: Cell | CellGroup,
        end_cell_group: Cell | CellGroup,
        off_limit_cells: frozenset[Cell] | None = None,
        other_cell_groups: frozenset[CellGroup] | None = None,
    ):
        """
        :param start_cell_group: The CellGroup that the path starts from.
        :param end_cell_group: The CellGroup where the path should end.
        :param off_limit_cells: Cells that the path cannot pass through. This can also be None which indicates that no
            cells are off limits.
        :param other_cell_groups: A set of other cell groups which are not a part of the start/end cell groups. If the
            path goes adjacent to a CellGroup in this set at least once, the "length" of the path increases by the
            number of cells in the CellGroup. Any remaining path steps through the CellGroup have zero "length". This
            can also be set to None which indicates that there are no other cell groups for which this rule should
            apply.

        """
        self.start_cell_group = self.to_cell_group(start_cell_group)
        self.end_cell_group = self.to_cell_group(end_cell_group)

        if off_limit_cells is None:
            self.off_limit_cells: frozenset[Cell] = frozenset()
        else:
            self.off_limit_cells = off_limit_cells

        if other_cell_groups is None:
            self.other_cell_groups: frozenset[CellGroup] = frozenset()
        else:
            self.other_cell_groups = other_cell_groups

        self.check_path_finding_setup()

    @staticmethod
    def to_cell_group(cell_or_cell_group: Cell | CellGroup) -> CellGroup:
        if isinstance(cell_or_cell_group, Cell):
            cell_group = CellGroup(cells={cell_or_cell_group})
        elif isinstance(cell_or_cell_group, CellGroup):
            cell_group = cell_or_cell_group
        else:
            msg = f'Unexpected type for cell_or_cell_group: {type(cell_or_cell_group)}'
            raise TypeError(msg)
        return cell_group

    def check_path_finding_setup(self) -> None:
        if len(self.start_cell_group.cells.intersection(self.off_limit_cells)) > 0:
            msg = 'Cannot find path since a cell in the start cell group is off limits'
            raise PathSetupError(msg)
        if len(self.end_cell_group.cells.intersection(self.off_limit_cells)) > 0:
            msg = 'Cannot find path since a cell in the end cell group is off limits'
            raise PathSetupError(msg)

        cells_adjacent_to_start_cell_group = self.start_cell_group.get_adjacent_neighbors()
        for other_cell_group in self.other_cell_groups:
            if len(other_cell_group.cells.intersection(cells_adjacent_to_start_cell_group)) > 0:
                msg = 'Start cell group is adjacent to a cell in the other_cell_groups'
                raise PathSetupError(msg)
            if len(other_cell_group.cells.intersection(self.off_limit_cells)) > 0:
                msg = 'An off limit cell is is also part of other_cell_groups'
                raise PathSetupError(msg)

        self.check_for_overlapping_other_cell_groups()

    def check_for_overlapping_other_cell_groups(self) -> None:
        cells_in_other_cell_groups: set[Cell] = set()
        for other_cell_group in self.other_cell_groups:
            if len(other_cell_group.cells.intersection(cells_in_other_cell_groups)) > 0:
                msg = 'There cannot be overlapping other cell groups'
                raise PathSetupError(msg)
            cells_in_other_cell_groups.update(other_cell_group.cells)

    def get_path_info(self, max_path_length: int | None = None) -> PathInfo:
        """
        Note that max_path_length includes both the start and end cell. If a path cannot be found from the start cell
        group to the end cell group, or the path can be found but is longer than the max path length, this function
        raises a NoPathFoundError exception.

        :param max_path_length: The max length of the path. Note that the path length includes both the start and end
            cell. This can also be None which indicates that there is no limit on the path length.
        :return: A PathInfo object which contains information about the path from the start cell group to the end cell
            group.
        """
        # The shortest possible path length is 1 plus the Manhattan distance between the closest cells in the two groups
        min_possible_path_length = self.start_cell_group.get_shortest_naive_path_length_to_cell_group(
            self.end_cell_group
        )
        if max_path_length is not None and min_possible_path_length > max_path_length:
            raise NoPathFoundError(self.get_no_path_error_string(max_path_length))

        # Keep a prioritized queue of cells to explore. Start with a random cell in the start cell group.
        prioritized_cells_to_explore: queue.PriorityQueue[PrioritizedCell] = queue.PriorityQueue()
        start_cell = next(iter(self.start_cell_group.cells))
        prioritized_cells_to_explore.put(PrioritizedCell(priority=min_possible_path_length, cell=start_cell))

        # Keep track of the details on how the path got from the start cell group to each cell. We can't just use a
        # simple map from each cell to its parent cell since the "length" of a step from cell A to cell B may depend on
        # the path taken to get to the cell A due to how adjacent cell groups are handled.
        path_info_to_cell: dict[Cell, PathInfo] = {start_cell: PathInfo(cell_list=[start_cell], path_length=1)}

        while not prioritized_cells_to_explore.empty():
            # Take the next cell to explore from the priority queue
            current_cell = prioritized_cells_to_explore.get().cell

            # If this cell is in the end_cell_group, then we have found the optimal path
            if current_cell in self.end_cell_group.cells:
                return path_info_to_cell[current_cell]

            # Get the list of non-off-limit cells that neighbor the current cell
            neighbor_cells_to_explore = [
                neighbor_cell
                for neighbor_cell in current_cell.get_adjacent_neighbors()
                if neighbor_cell not in self.off_limit_cells
            ]

            unvisited_other_cell_groups = self.other_cell_groups - path_info_to_cell[current_cell].adjacent_cell_groups
            for neighbor_cell in neighbor_cells_to_explore:
                distance_from_current_to_neighbor = self.get_distance_between_cells(current_cell, neighbor_cell)
                newly_adjacent_cell_groups = self.get_adjacent_cell_groups(neighbor_cell, unvisited_other_cell_groups)
                size_of_newly_adjacent_cell_groups = sum(
                    len(newly_adjacent_cell_group.cells) for newly_adjacent_cell_group in newly_adjacent_cell_groups
                )
                distance_from_current_to_neighbor += size_of_newly_adjacent_cell_groups

                # Determine the tentative g-score for the neighbor using the current best known optimal path to the
                # neighbor cell through the current cell
                tentative_g_score = path_info_to_cell[current_cell].path_length + distance_from_current_to_neighbor

                # If the tentative g-score is larger than the max allowed path length, then this potential path is not
                # viable
                if max_path_length is not None and tentative_g_score > max_path_length:
                    continue

                # Check if we already have found a shorter potential path length that goes through this neighbor cell.
                # If not, then we should extend the current path we are exploring through the neighbor cell by adding it
                # to the priority queue.
                if neighbor_cell in path_info_to_cell:
                    existing_g_score_for_neighbor = float(path_info_to_cell[neighbor_cell].path_length)
                else:
                    existing_g_score_for_neighbor = math.inf
                if tentative_g_score < existing_g_score_for_neighbor:
                    # This path is better than any previous one, so save the info on how we got here
                    path_info_to_neighbor_cell = path_info_to_cell[current_cell].get_extended_path_info(
                        new_cell=neighbor_cell,
                        additional_path_length=distance_from_current_to_neighbor,
                        additional_adjacent_cell_groups=newly_adjacent_cell_groups,
                    )
                    path_info_to_cell[neighbor_cell] = path_info_to_neighbor_cell

                    # Set the priority for exploring this neighbor cell further. The priority is the shortest known path
                    # length to get to this neighbor cell, plus the minimum possible distance to go from the neighbor
                    # cell to the end cell group
                    min_possible_remaining_distance = self.get_min_possible_remaining_distance(neighbor_cell)
                    f_score = tentative_g_score + min_possible_remaining_distance
                    cells_in_prioritized_cells_to_explore = {
                        prioritized_cell.cell for prioritized_cell in prioritized_cells_to_explore.queue
                    }

                    # TODO: I think we need to replace in the priority queue even if it's already there.
                    #  Or do we - since if we're finding the same path it maybe can't be shorter??
                    if neighbor_cell not in cells_in_prioritized_cells_to_explore:
                        prioritized_cells_to_explore.put(PrioritizedCell(priority=f_score, cell=neighbor_cell))

        raise NoPathFoundError(self.get_no_path_error_string(max_path_length))

    def get_distance_between_cells(self, current_cell: Cell, neighbor_cell: Cell) -> int:
        """Get the distance between the current cell and the neighbor cell."""
        if current_cell in self.start_cell_group.cells and neighbor_cell in self.start_cell_group.cells:
            # If both the current and the neighbor cell are part of the start_cell_group, then the distance is
            # considered zero
            distance_between_cells = 0
        elif any(neighbor_cell in other_cell_group.cells for other_cell_group in self.other_cell_groups):
            # Once the path steps adjacent to a cell in the other_cell_groups, the size of the cell group is added to
            # the path "length". Further steps into the cell group have zero additional cost. Therefore, if the neighbor
            # cell is part of the other_cell_groups, then the "distance" is zero. Note that this does not apply to
            # stepping out of a cell group to another cell that is not part of the other_cell_groups.
            distance_between_cells = 0
        else:
            distance_between_cells = 1

        return distance_between_cells

    @staticmethod
    def get_adjacent_cell_groups(root_cell: Cell, unvisited_other_cell_groups: frozenset[CellGroup]) -> set[CellGroup]:
        root_cell_adjacent_neighbors = root_cell.get_adjacent_neighbors()
        return {
            cell_group
            for cell_group in unvisited_other_cell_groups
            if cell_group.does_include_cell(root_cell_adjacent_neighbors)
        }

    def get_min_possible_remaining_distance(self, neighbor_cell: Cell) -> int:
        cell_group_containing_neighbor_cell: CellGroup | None = None
        for cell_group in self.other_cell_groups:
            if neighbor_cell in cell_group.cells:
                cell_group_containing_neighbor_cell = cell_group
                break
        if cell_group_containing_neighbor_cell is None:
            neighbor_cell_group = CellGroup(cells={neighbor_cell})
        else:
            neighbor_cell_group = cell_group_containing_neighbor_cell
        return neighbor_cell_group.get_shortest_manhattan_distance_to_cell_group(self.end_cell_group)

    def get_no_path_error_string(self, max_path_length: int | None) -> str:
        error_string = f'No viable path found from {self.start_cell_group} to {self.end_cell_group}'
        if max_path_length is not None:
            error_string += f' of length {max_path_length}'
        return error_string
