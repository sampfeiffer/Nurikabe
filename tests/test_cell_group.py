from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell import Cell
from nurikabe.cell_group import CellGroup, MultipleCluesInCellGroupError, NoCluesInCellGroupError


class TestCellGroup(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')
        cls.pixel_position = MagicMock(name='PixelPosition')

    def get_cell(self, row_number: int = 0, col_number: int = 0, clue: int | None = None) -> Cell:
        return Cell(row_number, col_number, clue, pixel_position=self.pixel_position, screen=self.screen)

    def test_contains_zero_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        cell_group_no_clues = CellGroup(cells)

        self.assertFalse(cell_group_no_clues.does_contain_clue())
        self.assertEqual(cell_group_no_clues.get_number_of_clues(), 0)
        with self.assertRaises(NoCluesInCellGroupError):
            cell_group_no_clues.get_clue_cell()
        with self.assertRaises(NoCluesInCellGroupError):
            cell_group_no_clues.get_clue_value()

    def test_contains_one_clue(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        clue_cell = self.get_cell(clue=10)
        cells.add(clue_cell)
        cell_group_one_clue = CellGroup(cells)

        self.assertTrue(cell_group_one_clue.does_contain_clue())
        self.assertEqual(cell_group_one_clue.get_number_of_clues(), 1)
        self.assertEqual(cell_group_one_clue.get_clue_cell(), clue_cell)
        self.assertEqual(cell_group_one_clue.get_clue_value(), 10)

    def test_contains_multiple_clues(self) -> None:
        cells = {self.get_cell(clue=None) for _ in range(5)}
        cells.add(self.get_cell(clue=10))
        cells.add(self.get_cell(clue=11))
        cell_group_multiple_clues = CellGroup(cells)

        self.assertTrue(cell_group_multiple_clues.does_contain_clue())
        self.assertEqual(cell_group_multiple_clues.get_number_of_clues(), 2)
        with self.assertRaises(MultipleCluesInCellGroupError):
            cell_group_multiple_clues.get_clue_cell()
        with self.assertRaises(MultipleCluesInCellGroupError):
            cell_group_multiple_clues.get_clue_value()

    def test_get_shortest_manhattan_distance_to_cell(self) -> None:
        cells_in_cell_group = {
            self.get_cell(row_number=5, col_number=4),
            self.get_cell(row_number=5, col_number=5),
            self.get_cell(row_number=6, col_number=5),
        }
        cell_group = CellGroup(cells_in_cell_group)

        destination_cell1 = self.get_cell(row_number=5, col_number=3)
        self.assertEqual(cell_group.get_shortest_manhattan_distance_to_cell(destination_cell1), 1)

        destination_cell2 = self.get_cell(row_number=5, col_number=6)
        self.assertEqual(cell_group.get_shortest_manhattan_distance_to_cell(destination_cell2), 1)

        destination_cell3 = self.get_cell(row_number=10, col_number=10)
        self.assertEqual(cell_group.get_shortest_manhattan_distance_to_cell(destination_cell3), 9)

        # Equidistant from more than one cell in the cell group
        destination_cell4 = self.get_cell(row_number=7, col_number=3)
        self.assertEqual(cell_group.get_shortest_manhattan_distance_to_cell(destination_cell4), 3)

        # Distance to a cell in the cell group should be 0
        destination_cell_in_cell_group = self.get_cell(row_number=5, col_number=5)
        self.assertEqual(cell_group.get_shortest_manhattan_distance_to_cell(destination_cell_in_cell_group), 0)

    def test_get_shortest_manhattan_distance_to_cell_group(self) -> None:
        cells_in_source_cell_group = {
            self.get_cell(row_number=5, col_number=4),
            self.get_cell(row_number=5, col_number=5),
            self.get_cell(row_number=6, col_number=5),
        }
        source_cell_group = CellGroup(cells_in_source_cell_group)

        cells_in_destination_cell_group1 = {
            self.get_cell(row_number=5, col_number=2),
            self.get_cell(row_number=6, col_number=2),
        }
        destination_cell_group1 = CellGroup(cells_in_destination_cell_group1)
        self.assertEqual(source_cell_group.get_shortest_manhattan_distance_to_cell_group(destination_cell_group1), 2)

        # Equidistant from more than one cell in the destination cell group
        cells_in_destination_cell_group2 = {
            self.get_cell(row_number=5, col_number=2),
            self.get_cell(row_number=6, col_number=3),
        }
        destination_cell_group2 = CellGroup(cells_in_destination_cell_group2)
        self.assertEqual(source_cell_group.get_shortest_manhattan_distance_to_cell_group(destination_cell_group2), 2)

        # Equidistant from more than one cell in the source cell group
        cells_in_destination_cell_group3 = {
            self.get_cell(row_number=7, col_number=2),
            self.get_cell(row_number=7, col_number=3),
        }
        destination_cell_group3 = CellGroup(cells_in_destination_cell_group3)
        self.assertEqual(source_cell_group.get_shortest_manhattan_distance_to_cell_group(destination_cell_group3), 3)

        # If the two cell groups contain any of the same cells, the distance should be zero
        cells_in_destination_cell_group4 = {
            self.get_cell(row_number=7, col_number=2),
            self.get_cell(row_number=6, col_number=5),
        }
        destination_cell_group4 = CellGroup(cells_in_destination_cell_group4)
        self.assertEqual(source_cell_group.get_shortest_manhattan_distance_to_cell_group(destination_cell_group4), 0)
