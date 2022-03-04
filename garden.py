from cell import Cell
from cell_state import CellState


class IncorrectGardenNumOfClues(Exception):
    pass


class Garden:
    """
    A garden is an isolated section of cells that are not walls (either empty or marked as non-wall). Being connected to
    something diagonally does not impact whether a garden is isolated
    """

    def __init__(self, cells: set[Cell]):
        self.cells = cells

    def does_have_exactly_one_clue(self) -> bool:
        return len([cell for cell in self.cells if cell.has_clue]) == 1

    def is_garden_correct_size(self) -> bool:
        return len(self.cells) == self.get_expected_garden_size()

    def get_expected_garden_size(self) -> int:
        if not self.does_have_exactly_one_clue():
            raise IncorrectGardenNumOfClues('Garden does not have exactly one clue')
        for cell in self.cells:
            if cell.has_clue:
                return cell.initial_value

    def paint_garden_if_completed(self) -> None:
        if self.does_have_exactly_one_clue() and self.is_garden_correct_size() and self.is_garden_full_of_non_walls():
            self.paint_completed_garden()

    def is_garden_full_of_non_walls(self) -> bool:
        return all(cell.cell_state is CellState.NON_WALL or cell.has_clue for cell in self.cells)

    def paint_completed_garden(self) -> None:
        for cell in self.cells:
            cell.paint_completed_cell()
