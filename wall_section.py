from cell import Cell
from cell_group import CellGroup
from cell_state import CellState


class WallSection(CellGroup):
    """
    A wall section is a section connected wall cells that are not walls. Being connected diagonally does not count as
    being connected.
    """

    def get_escape_routes(self) -> list[Cell]:
        adjacent_neighbors = self.get_adjacent_neighbors()
        return [cell for cell in adjacent_neighbors if cell.cell_state == CellState.EMPTY and not cell.has_clue]

    def get_adjacent_neighbors(self) -> set[Cell]:
        list_neighbor_cell_list: list[list[Cell]] = [cell.get_adjacent_neighbors() for cell in self.cells]
        return {cell for neighbor_list in list_neighbor_cell_list for cell in neighbor_list}
