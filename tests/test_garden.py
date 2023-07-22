from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell import Cell
from nurikabe.cell_group import NoCluesInCellGroupError, MultipleCluesInCellGroupError
from nurikabe.garden import Garden


class TestGarden(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')
        cls.pixel_position = MagicMock(name='PixelPosition')

    def get_cell(self, row_number: int = 0, col_number: int = 0, clue: Optional[int] = None) -> Cell:
        return Cell(row_number, col_number, clue, pixel_position=self.pixel_position, screen=self.screen)

    def test_garden_no_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        garden_no_clues = Garden(cells)

        with self.assertRaises(NoCluesInCellGroupError):
            self.assertFalse(garden_no_clues.get_num_of_remaining_garden_cells())

    def test_garden_one_clue(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        clue_cell10 = self.get_cell(clue=10)
        garden_one_clue = Garden(cells.union({clue_cell10}))

        self.assertEqual(garden_one_clue.get_num_of_remaining_garden_cells(), 4)

    def test_weak_garden_multiple_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        clue_cell1 = self.get_cell(clue=10)
        clue_cell2 = self.get_cell(clue=15)
        garden_multiple_clues = Garden(cells.union({clue_cell1, clue_cell2}))

        with self.assertRaises(MultipleCluesInCellGroupError):
            garden_multiple_clues.get_num_of_remaining_garden_cells()
