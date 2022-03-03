from cell import Cell


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
        return len([cell for cell in self.cells if cell.initial_value is not None]) == 1

    def is_garden_correct_size(self) -> bool:
        return len(self.cells) == self.get_expected_garden_size()

    def get_expected_garden_size(self) -> int:
        if not self.does_have_exactly_one_clue():
            raise IncorrectGardenNumOfClues('Garden does not have exactly one clue')
        for cell in self.cells:
            if cell.initial_value is not None:
                return cell.initial_value
