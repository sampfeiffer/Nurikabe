import queue
import math
from dataclasses import dataclass, field
from typing import Optional

from cell import Cell


class NoPathFoundError(Exception):
    pass


@dataclass(order=True)
class PrioritizedCell:
    priority: int
    cell: Cell = field(compare=False)


def find_shortest_path(start_cell: Cell, end_cell: Cell, off_limits_cells: set[Cell],
                       max_path_length: Optional[int] = None) -> list[Cell]:
    """
    Uses A* algorithm. https://en.wikipedia.org/wiki/A*_search_algorithm

    The heuristic get_shortest_naive_path_length is admissible meaning that this length is never greater than the actual
    shortest path length. The heuristic is also consistent since the heuristic changes by a value of 1 every time we
    move one cell away from the current cell.
    """

    if start_cell in off_limits_cells or end_cell in off_limits_cells:
        raise NoPathFoundError('Cannot find path since start or end cell is off limits')

    min_possible_path_length = start_cell.get_shortest_naive_path_length(end_cell)
    if max_path_length is not None and min_possible_path_length > max_path_length:
        raise NoPathFoundError(get_no_path_error_string(start_cell, end_cell, max_path_length))

    prioritized_cells_to_explore: queue.PriorityQueue[PrioritizedCell] = queue.PriorityQueue()
    prioritized_cells_to_explore.put(PrioritizedCell(priority=0, cell=start_cell))

    map_to_parent_cell: dict[Cell, Cell] = {}

    # Called g-score in the wiki page
    path_length_from_start_cell: dict[Cell, int] = {start_cell: 0}

    # For each cell, this is the current best guess for the shortest possible path length from start_cell to end_cell
    # that passes through this cell. Called f-score in the wiki page.
    best_guess_shortest_path_length_through_cell: dict[Cell, int] = {start_cell: min_possible_path_length}

    while not prioritized_cells_to_explore.empty():
        current_cell = prioritized_cells_to_explore.get().cell
        if current_cell is end_cell:
            return reconstruct_path(map_to_parent_cell, current_cell)

        neighbor_cells_to_explore = [neighbor_cell for neighbor_cell in current_cell.get_adjacent_neighbors()
                                     if neighbor_cell not in off_limits_cells]
        for neighbor_cell in neighbor_cells_to_explore:
            tentative_g_score = path_length_from_start_cell[current_cell] + 1
            if max_path_length is not None and tentative_g_score > max_path_length:
                continue
            existing_g_score_for_neighbor = path_length_from_start_cell.get(neighbor_cell, math.inf)
            if tentative_g_score < existing_g_score_for_neighbor:
                # This path is better than any previous one
                map_to_parent_cell[neighbor_cell] = current_cell
                path_length_from_start_cell[neighbor_cell] = tentative_g_score
                f_score = tentative_g_score + neighbor_cell.get_shortest_naive_path_length(end_cell)
                best_guess_shortest_path_length_through_cell[neighbor_cell] = f_score
                cells_in_prioritized_cells_to_explore = {
                    prioritized_cell.cell for prioritized_cell in prioritized_cells_to_explore.queue
                }
                if neighbor_cell not in cells_in_prioritized_cells_to_explore:
                    prioritized_cells_to_explore.put(PrioritizedCell(priority=f_score, cell=neighbor_cell))

    raise NoPathFoundError(get_no_path_error_string(start_cell, end_cell, max_path_length))


def reconstruct_path(map_to_parent_cell: dict[Cell, Cell], end_cell: Cell) -> list[Cell]:
    current_cell = end_cell
    reversed_path = [current_cell]
    while current_cell in map_to_parent_cell.keys():
        current_cell = map_to_parent_cell[current_cell]
        reversed_path.append(current_cell)
    return reversed_path[::-1]  # reverse the path so it faces the right direction


def get_no_path_error_string(start_cell: Cell, end_cell: Cell, max_path_length: Optional[int]) -> str:
    error_string = f'No viable path found from {start_cell} to {end_cell}'
    if max_path_length is not None:
        error_string += f' of length {max_path_length}'
    return error_string
