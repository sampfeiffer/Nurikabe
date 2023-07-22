from typing import Callable

from .cell import Cell


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
        number_of_clues = self.get_number_of_clues()
        if number_of_clues == 0:
            raise RuntimeError('Cannot get clue value since there are no clues in this CellGroup')
        elif number_of_clues > 1:
            raise RuntimeError('CellGroup has more than 1 clue')
        else:
            for cell in self.cells:
                if cell.has_clue:
                    return cell.clue
        raise RuntimeError('It should not be possible to reach this code')

    def get_shortest_manhattan_distance_to_cell(self, destination_cell: Cell) -> int:
        return min([source_cell.get_manhattan_distance(destination_cell) for source_cell in self.cells])
