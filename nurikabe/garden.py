from collections.abc import Callable

from .cell import Cell
from .weak_garden import WeakGarden


class Garden(WeakGarden):
    """
    A garden is a connected section of cells that are strictly not walls (either marked as a non-wall cell or a clue
    cell). Note that this is a stricter version of a weak garden since a weak garden can also contain empty cells. Being
    connected to something diagonally does not count as connected.
    """

    @staticmethod
    def is_garden_static(cell: Cell) -> bool:
        return cell.cell_state.is_garden()

    @staticmethod
    def get_cell_criteria_func() -> Callable[[Cell], bool]:
        return Garden.is_garden_static

    def get_num_of_remaining_garden_cells(self) -> int:
        expected_garden_size = self.get_expected_garden_size()
        return expected_garden_size - len(self.cells)

    def paint_garden_if_completed(self) -> None:
        if self.does_have_exactly_one_clue() and self.is_garden_correct_size() and self.is_garden_fully_enclosed():
            self.paint_completed_garden()

    def is_garden_fully_enclosed(self) -> bool:
        return all(cell.cell_state.is_wall() for cell in self.get_adjacent_neighbors())

    def paint_completed_garden(self) -> None:
        for cell in self.cells:
            cell.paint_completed_cell()
