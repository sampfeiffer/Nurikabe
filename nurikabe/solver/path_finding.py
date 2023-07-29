import queue
import math
from dataclasses import dataclass, field
from typing import Optional

from ..cell import Cell
from ..cell_group import CellGroup


class NoPathFoundError(Exception):
    pass


@dataclass(order=True)
class PrioritizedCell:
    priority: int
    cell: Cell = field(compare=False)


def find_shortest_path_between_cells(start_cell: Cell, end_cell: Cell, off_limits_cells: set[Cell],
                                     max_path_length: Optional[int] = None) -> list[Cell]:
    start_cell_group = CellGroup(cells={start_cell})
    end_cell_group = CellGroup(cells={end_cell})
    return find_shortest_path_between_cell_groups(start_cell_group, end_cell_group, off_limits_cells, max_path_length)


def find_shortest_path_cell_group_to_cell(start_cell_group: CellGroup, end_cell: Cell, off_limits_cells: set[Cell],
                                          max_path_length: Optional[int] = None) -> list[Cell]:
    end_cell_group = CellGroup(cells={end_cell})
    return find_shortest_path_between_cell_groups(start_cell_group, end_cell_group, off_limits_cells, max_path_length)


def find_shortest_path_cell_to_cell_group(start_cell: Cell, end_cell_group: CellGroup, off_limits_cells: set[Cell],
                                          max_path_length: Optional[int] = None) -> list[Cell]:
    start_cell_group = CellGroup(cells={start_cell})
    return find_shortest_path_between_cell_groups(start_cell_group, end_cell_group, off_limits_cells, max_path_length)


def find_shortest_path_between_cell_groups(start_cell_group: CellGroup, end_cell_group: CellGroup,
                                           off_limits_cells: set[Cell],
                                           max_path_length: Optional[int] = None) -> list[Cell]:
    """
    Uses A* algorithm. https://en.wikipedia.org/wiki/A*_search_algorithm

    The heuristic get_shortest_naive_path_length_to_cell_group is admissible meaning that this length is never greater
    than the actual shortest path length. The heuristic is also consistent since the when going from two neighboring
    cells, the change in heuristic never overestimates the actual cost of the step.
    """

    if len(start_cell_group.cells.intersection(off_limits_cells)) > 0:
        raise NoPathFoundError('Cannot find path since a cell in the start cell group is off limits')
    if len(end_cell_group.cells.intersection(off_limits_cells)) > 0:
        raise NoPathFoundError('Cannot find path since a cell in the end cell group is off limits')

    # The shortest possible path length is 1 plus the Manhattan distance between the closest cells in the two groups
    min_possible_path_length = start_cell_group.get_shortest_naive_path_length_to_cell_group(end_cell_group)
    if max_path_length is not None and min_possible_path_length > max_path_length:
        raise NoPathFoundError(get_no_path_error_string(start_cell_group, end_cell_group, max_path_length))

    # Keep a prioritized queue of cells to explore. Start with a random cell in the start cell group.
    prioritized_cells_to_explore: queue.PriorityQueue[PrioritizedCell] = queue.PriorityQueue()
    start_cell = list(start_cell_group.cells)[0]
    prioritized_cells_to_explore.put(PrioritizedCell(priority=0, cell=start_cell))

    # Keep track of the parent cell from each cell so that if/when the path finding algorithm finds the shortest
    # possible path, we can back out the list of cells that make up this path
    map_to_parent_cell: dict[Cell, Cell] = {}

    # Called g-score in the wiki page
    path_length_from_start_cell: dict[Cell, int] = {start_cell: 0}

    # For each cell, this is the current best guess for the shortest possible path length from start_cell_group to
    # end_cell_group that passes through this cell. Called f-score in the wiki page.
    best_guess_shortest_path_length_through_cell: dict[Cell, int] = {start_cell: min_possible_path_length}

    while not prioritized_cells_to_explore.empty():
        # Take the next cell to explore from the priority queue
        current_cell = prioritized_cells_to_explore.get().cell

        # If this cell is in the end_cell_group, then we have found the optimal path
        if current_cell in end_cell_group.cells:
            return reconstruct_path(map_to_parent_cell, current_cell)

        # Get the list of non-off-limit cells that neighbor the current cell
        neighbor_cells_to_explore = [neighbor_cell for neighbor_cell in current_cell.get_adjacent_neighbors()
                                     if neighbor_cell not in off_limits_cells]

        for neighbor_cell in neighbor_cells_to_explore:
            distance_from_current_to_neighbor = get_distance_between_cells(current_cell, neighbor_cell,
                                                                           start_cell_group)

            # Determine the tentative g-score for the neighbor using the current best known optimal path to the neighbor
            # cell through the current cell
            tentative_g_score = path_length_from_start_cell[current_cell] + distance_from_current_to_neighbor

            # If the tentative g-score is larger than the max allowed path length, then this potential path is not
            # viable
            if max_path_length is not None and tentative_g_score > max_path_length:
                continue

            # Check if we already have found a shorter potential path length that goes through this neighbor cell. If
            # not, then we should extend the current path we are exploring through the neighbor cell by adding it to the
            # priority queue.
            existing_g_score_for_neighbor = path_length_from_start_cell.get(neighbor_cell, math.inf)
            if tentative_g_score < existing_g_score_for_neighbor:
                # This path is better than any previous one, so save the info on how we got here
                map_to_parent_cell[neighbor_cell] = current_cell
                path_length_from_start_cell[neighbor_cell] = tentative_g_score

                # Set the priority for exploring this neighbor cell further. The priority is the shortest known path
                # length to get to this neighbor cell, plus the minimum possible path length to go from the neighbor
                # cell to the end cell group
                f_score = tentative_g_score + end_cell_group.get_shortest_naive_path_length_to_cell(neighbor_cell)
                best_guess_shortest_path_length_through_cell[neighbor_cell] = f_score
                cells_in_prioritized_cells_to_explore = {
                    prioritized_cell.cell for prioritized_cell in prioritized_cells_to_explore.queue
                }
                if neighbor_cell not in cells_in_prioritized_cells_to_explore:
                    prioritized_cells_to_explore.put(PrioritizedCell(priority=f_score, cell=neighbor_cell))

    raise NoPathFoundError(get_no_path_error_string(start_cell_group, end_cell_group, max_path_length))


def get_distance_between_cells(current_cell: Cell, neighbor_cell: Cell, start_cell_group: CellGroup) -> int:
    """
    Get the distance between the current cell and the neighbor cell. If they are both part of the start_cell_group, then
    the distance is considered zero. Otherwise, the distance is one.
    """

    if current_cell in start_cell_group and neighbor_cell in start_cell_group:
        return 0
    else:
        return 1


def reconstruct_path(map_to_parent_cell: dict[Cell, Cell], end_cell: Cell) -> list[Cell]:
    current_cell = end_cell
    reversed_path = [current_cell]
    while current_cell in map_to_parent_cell.keys():
        current_cell = map_to_parent_cell[current_cell]
        reversed_path.append(current_cell)
    return reversed_path[::-1]  # reverse the path so it faces the right direction


def get_no_path_error_string(start_cell_group: CellGroup, end_cell_group: CellGroup,
                             max_path_length: Optional[int]) -> str:
    error_string = f'No viable path found from {start_cell_group} to {end_cell_group}'
    if max_path_length is not None:
        error_string += f' of length {max_path_length}'
    return error_string
