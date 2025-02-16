from .cell_group import CellGroup


class WeakGarden(CellGroup):
    """
    A weak garden is a connected section of cells that are not walls (empty, clue, or marked as non-wall). Being
    connected to something diagonally does not count as connected.
    """

    def does_have_exactly_one_clue(self) -> bool:
        return self.get_number_of_clues() == 1

    def is_garden_correct_size(self) -> bool:
        return len(self.cells) == self.get_expected_garden_size()

    def get_expected_garden_size(self) -> int:
        return self.get_clue_value()

    def has_non_wall_cell(self) -> bool:
        return any(cell.cell_state.is_non_wall() for cell in self.cells)
