from cell import Cell


class CellGroup:
    def __init__(self, cells: set[Cell]):
        self.cells = cells

    def get_empty_adjacent_neighbors(self) -> set[Cell]:
        adjacent_neighbors = self.get_adjacent_neighbors()
        return {cell for cell in adjacent_neighbors if cell.cell_state.is_empty()}

    def get_adjacent_neighbors(self) -> set[Cell]:
        list_neighbor_cell_list: list[list[Cell]] = [cell.get_adjacent_neighbors() for cell in self.cells]
        return {cell for neighbor_list in list_neighbor_cell_list for cell in neighbor_list}

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
