from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell import Cell


class TestCell(TestCase):
    def setUp(self) -> None:
        self.screen = MagicMock(name='Screen')

    def test_get_manhattan_distance(self) -> None:
        pixel_position = MagicMock(name='PixelPosition')
        cell1 = Cell(row_number=5, col_number=10, clue=None, pixel_position=pixel_position, screen=self.screen)
        cell2 = Cell(row_number=0, col_number=11, clue=None, pixel_position=pixel_position, screen=self.screen)
        manhattan_distance = cell1.get_manhattan_distance(cell2)
        self.assertEqual(manhattan_distance, 6)

    def test_get_shortest_naive_path_length(self) -> None:
        pixel_position = MagicMock(name='PixelPosition')
        cell1 = Cell(row_number=5, col_number=10, clue=None, pixel_position=pixel_position, screen=self.screen)
        cell2 = Cell(row_number=0, col_number=7, clue=None, pixel_position=pixel_position, screen=self.screen)
        shortest_naive_path_length = cell1.get_shortest_naive_path_length(cell2)
        self.assertEqual(shortest_naive_path_length, 9)
