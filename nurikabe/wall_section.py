from typing import Callable

from cell_group import CellGroup
from cell import Cell


class WallSection(CellGroup):
    """
    A wall section is a connected section of wall cells. Being connected diagonally does not count as being connected.
    """

    @staticmethod
    def get_cell_criteria_func() -> Callable[[Cell], bool]:
        return lambda cell: cell.cell_state.is_wall()
