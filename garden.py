from typing import Optional

from cell_group import CellGroup


class Garden(CellGroup):
    """
    A garden is a connected section of cells that are not walls (either empty or marked as non-wall). Being connected to
    something diagonally does not count as connected.

    Some terminology:
    A StrictGarden is a Garden that only includes cells marked as a non-wall and clue cells.
    An incomplete strict Garden is a strict garden that is not fully enclosed by walls.
    """

    def does_have_exactly_one_clue(self) -> bool:
        return len([cell for cell in self.cells if cell.has_clue]) == 1

    def is_garden_correct_size(self) -> bool:
        return len(self.cells) == self.get_expected_garden_size()

    def get_expected_garden_size(self) -> Optional[int]:
        for cell in self.cells:
            if cell.has_clue:
                return cell.clue
        return None

    def paint_garden_if_completed(self) -> None:
        if self.does_have_exactly_one_clue() and self.is_garden_correct_size() and self.is_garden_full_of_non_walls():
            self.paint_completed_garden()

    def is_garden_full_of_non_walls(self) -> bool:
        return all(cell.cell_state.is_non_wall_or_clue() for cell in self.cells)

    def paint_completed_garden(self) -> None:
        for cell in self.cells:
            cell.paint_completed_cell()
