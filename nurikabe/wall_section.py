from collections.abc import Callable

from .cell import Cell
from .cell_group import CellGroup


class WallSection(CellGroup):
    """
    A wall section is a connected section of wall cells. Being connected diagonally does not count as being connected.
    """

    @staticmethod
    def is_wall_section_static(cell: Cell) -> bool:
        return cell.cell_state.is_wall()

    @staticmethod
    def get_cell_criteria_func() -> Callable[[Cell], bool]:
        return WallSection.is_wall_section_static
