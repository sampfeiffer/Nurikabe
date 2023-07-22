from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell import Cell
from nurikabe.cell_group import NoCluesInCellGroupError, MultipleCluesInCellGroupError
from nurikabe.weak_garden import WeakGarden


class TestWeakGarden(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')
        cls.pixel_position = MagicMock(name='PixelPosition')

    def get_cell(self, row_number: int = 0, col_number: int = 0, clue: Optional[int] = None) -> Cell:
        return Cell(row_number, col_number, clue, pixel_position=self.pixel_position, screen=self.screen)

    def test_weak_garden_no_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        weak_garden_no_clues = WeakGarden(cells)

        self.assertFalse(weak_garden_no_clues.does_have_exactly_one_clue())

        with self.assertRaises(NoCluesInCellGroupError):
            weak_garden_no_clues.get_expected_garden_size()

        with self.assertRaises(NoCluesInCellGroupError):
            weak_garden_no_clues.is_garden_correct_size()

    def test_weak_garden_one_clue(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        clue_cell10 = self.get_cell(clue=10)
        weak_garden_one_clue = WeakGarden(cells.union({clue_cell10}))

        self.assertTrue(weak_garden_one_clue.does_have_exactly_one_clue())
        self.assertEquals(weak_garden_one_clue.get_expected_garden_size(), 10)
        self.assertFalse(weak_garden_one_clue.is_garden_correct_size())

        clue_cell6 = self.get_cell(clue=6)
        weak_garden_correct_size = WeakGarden(cells.union({clue_cell6}))
        self.assertTrue(weak_garden_correct_size.is_garden_correct_size())

    def test_weak_garden_multiple_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        clue_cell1 = self.get_cell(clue=10)
        clue_cell2 = self.get_cell(clue=15)
        weak_garden_multiple_clues = WeakGarden(cells.union({clue_cell1, clue_cell2}))

        self.assertFalse(weak_garden_multiple_clues.does_have_exactly_one_clue())

        with self.assertRaises(MultipleCluesInCellGroupError):
            weak_garden_multiple_clues.get_expected_garden_size()

        with self.assertRaises(MultipleCluesInCellGroupError):
            weak_garden_multiple_clues.is_garden_correct_size()