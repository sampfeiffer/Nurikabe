from typing import Optional, Callable

from .cell_group import CellGroup
from .cell import Cell


class WeakGarden(CellGroup):
    """
    A weak garden is a connected section of cells that are not walls (empty, clue, or marked as non-wall). Being
    connected to something diagonally does not count as connected.
    """

    @staticmethod
    def get_cell_criteria_func() -> Callable[[Cell], bool]:
        return lambda cell: cell.cell_state.is_weak_garden()

    def does_have_exactly_one_clue(self) -> bool:
        return len([cell for cell in self.cells if cell.has_clue]) == 1

    def is_garden_correct_size(self) -> bool:
        return len(self.cells) == self.get_expected_garden_size()

    def get_expected_garden_size(self) -> Optional[int]:
        for cell in self.cells:
            if cell.has_clue:
                return cell.clue
        return None

    def get_clue_cell(self) -> Cell:
        if not self.does_have_exactly_one_clue():
            raise RuntimeError('Does not contain exactly one clue')
        for cell in self.cells:
            if cell.has_clue:
                return cell

        raise RuntimeError('This should not be reachable code')
