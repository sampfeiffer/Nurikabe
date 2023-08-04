from __future__ import annotations
from typing import Callable

from .cell import Cell
from .rect_edge import RectEdge
from .color import Color
from .screen import Screen


class NoCluesInCellGroupError(Exception):
    pass


class MultipleCluesInCellGroupError(Exception):
    pass


class CellGroup:
    @staticmethod
    def get_cell_criteria_func() -> Callable[[Cell], bool]:
        raise NotImplementedError('Unknown criteria for general CellGroup')

    def __init__(self, cells: set[Cell]):
        self.cells = cells

    def get_empty_adjacent_neighbors(self) -> set[Cell]:
        adjacent_neighbors = self.get_adjacent_neighbors()
        return {cell for cell in adjacent_neighbors if cell.cell_state.is_empty()}

    def get_adjacent_neighbors(self) -> set[Cell]:
        list_of_neighbor_cell_sets: list[set[Cell]] = [cell.get_adjacent_neighbors() for cell in self.cells]
        return {cell for neighbor_cells in list_of_neighbor_cell_sets
                for cell in neighbor_cells if cell not in self.cells}

    def does_contain_clue(self) -> bool:
        return self.get_number_of_clues() > 0

    def get_number_of_clues(self) -> int:
        return len([cell for cell in self.cells if cell.has_clue])

    def get_clue_value(self) -> int:
        return self.get_clue_cell().clue

    def get_clue_cell(self) -> Cell:
        number_of_clues = self.get_number_of_clues()
        if number_of_clues == 0:
            raise NoCluesInCellGroupError('Cannot get clue cell since there are no clues in this CellGroup')
        elif number_of_clues > 1:
            raise MultipleCluesInCellGroupError('CellGroup has more than 1 clue')
        else:
            for cell in self.cells:
                if cell.has_clue:
                    return cell
        raise RuntimeError('It should not be possible to reach this code')

    def does_contain_wall(self) -> bool:
        return any(cell.cell_state.is_wall() for cell in self.cells)

    def get_shortest_manhattan_distance_to_cell(self, destination_cell: Cell) -> int:
        return min([source_cell.get_manhattan_distance(destination_cell) for source_cell in self.cells])

    def get_shortest_naive_path_length_to_cell(self, destination_cell: Cell) -> int:
        return self.get_shortest_manhattan_distance_to_cell(destination_cell) + 1

    def get_shortest_manhattan_distance_to_cell_group(self, destination_cell_group: CellGroup) -> int:
        return min([self.get_shortest_manhattan_distance_to_cell(cell_in_destination_group)
                    for cell_in_destination_group in destination_cell_group.cells])

    def get_shortest_naive_path_length_to_cell_group(self, destination_cell_group: CellGroup) -> int:
        return self.get_shortest_manhattan_distance_to_cell_group(destination_cell_group) + 1

    def draw_edges(self, screen: Screen, color: Color) -> None:
        for edge in self.get_edges():
            screen.draw_edge(edge, color, width=2)

    def get_edges(self) -> set[RectEdge]:
        """
        Get the set of edges of the cell group. Note that this just includes the outer edges. It does not include the
        cell edges that are common to more than one cell in the cell group.
        """
        all_cell_edges = [rect_edge for cell in self.cells for rect_edge in cell.get_edges()]
        return {cell_edges for cell_edges in all_cell_edges if all_cell_edges.count(cell_edges) == 1}

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        cell_string_set = {str(cell) for cell in self.cells}
        return f'{class_name}(cells={cell_string_set})'
