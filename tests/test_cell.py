from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell import Cell, NonExistentNeighbor
from nurikabe.cell_state import CellState
from nurikabe.direction import Direction


class TestCell(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')
        cls.pixel_position = MagicMock(name='PixelPosition')

    def get_cell(self, row_number: int = 0, col_number: int = 0, clue: Optional[int] = None) -> Cell:
        return Cell(row_number, col_number, clue, pixel_position=self.pixel_position, screen=self.screen)


class TestCellDistance(TestCell):
    def test_get_manhattan_distance(self) -> None:
        cell1 = self.get_cell(row_number=5, col_number=10)
        cell2 = self.get_cell(row_number=0, col_number=11)
        self.assertEqual(cell1.get_manhattan_distance(cell2), 6)

        # Should be the same in either direction
        self.assertEqual(cell1.get_manhattan_distance(cell2), cell2.get_manhattan_distance(cell1))

    def test_get_shortest_naive_path_length(self) -> None:
        cell1 = self.get_cell(row_number=5, col_number=10)
        cell2 = self.get_cell(row_number=0, col_number=7)
        manhattan_distance = cell1.get_manhattan_distance(cell2)
        shortest_naive_path_length = cell1.get_shortest_naive_path_length(cell2)
        self.assertEqual(manhattan_distance, 8)
        self.assertEqual(shortest_naive_path_length, 9)


class TestCellState(TestCell):
    def test_cell_state_cycle(self) -> None:
        cell = self.get_cell(clue=None)

        # cell should start empty
        self.assertIs(cell.cell_state, CellState.EMPTY)

        # Click once. Now it should be a wall
        cell.handle_cell_click()
        self.assertIs(cell.cell_state, CellState.WALL)

        # Click again. Now it should be a non-wall
        cell.handle_cell_click()
        self.assertIs(cell.cell_state, CellState.NON_WALL)

        # Click again. Now it should be back to empty
        cell.handle_cell_click()
        self.assertIs(cell.cell_state, CellState.EMPTY)

    def test_clue_cell(self) -> None:
        cell = self.get_cell(clue=5)

        self.assertIs(cell.cell_state, CellState.CLUE)

        # Clicking should not impact the state of the cell since it is not clickable
        cell.handle_cell_click()
        self.assertIs(cell.cell_state, CellState.CLUE)


class TestCellNeighbors(TestCell):
    def test_get_neighbor_methods(self) -> None:
        cell = self.get_cell()

        # Note that we're not including Direction.LEFT_DOWN
        neighbor_cell_map = {
            Direction.LEFT_UP: self.get_cell(),
            Direction.UP: self.get_cell(),
            Direction.RIGHT_UP: self.get_cell(),
            Direction.RIGHT: self.get_cell(),
            Direction.RIGHT_DOWN: self.get_cell(),
            Direction.DOWN: self.get_cell(),
            Direction.LEFT: self.get_cell()
        }
        cell.set_neighbor_map(neighbor_cell_map)

        # Check if getting neighbors returns the correct ones
        up_and_right_up_neighbors = cell.get_neighbor_set({Direction.UP, Direction.RIGHT_UP})
        expected = {neighbor_cell_map[Direction.UP], neighbor_cell_map[Direction.RIGHT_UP]}
        self.assertEqual(up_and_right_up_neighbors, expected)

        # Attempting to get a neighbor set that includes a non-existent neighbor throws an error
        with self.assertRaises(NonExistentNeighbor):
            cell.get_neighbor_set({Direction.UP, Direction.LEFT_DOWN})

    def test_get_adjacent_neighbors(self) -> None:
        cell = self.get_cell()

        # Note that we're not including anything in the down direction
        neighbor_cell_map = {
            Direction.LEFT_UP: self.get_cell(),
            Direction.UP: self.get_cell(),
            Direction.RIGHT_UP: self.get_cell(),
            Direction.RIGHT: self.get_cell(),
            Direction.LEFT: self.get_cell()
        }
        cell.set_neighbor_map(neighbor_cell_map)

        adjacent_neighbors = cell.get_adjacent_neighbors()
        expected = {neighbor_cell_map[Direction.UP], neighbor_cell_map[Direction.RIGHT],
                    neighbor_cell_map[Direction.LEFT]}
        self.assertEqual(adjacent_neighbors, expected)

    def test_two_by_two_section(self) -> None:
        cell = self.get_cell()

        neighbor_cell_map = {
            Direction.LEFT_UP: self.get_cell(),
            Direction.UP: self.get_cell(),
            Direction.RIGHT_UP: self.get_cell(),
            Direction.RIGHT: self.get_cell(),
            Direction.RIGHT_DOWN: self.get_cell(),
            Direction.DOWN: self.get_cell(),
            Direction.LEFT_DOWN: self.get_cell(),
            Direction.LEFT: self.get_cell()
        }
        cell.set_neighbor_map(neighbor_cell_map)

        two_by_two_section = cell.get_two_by_two_section()
        expected = {cell, neighbor_cell_map[Direction.RIGHT], neighbor_cell_map[Direction.RIGHT_DOWN],
                    neighbor_cell_map[Direction.DOWN]}
        self.assertEqual(two_by_two_section, expected)

    def test_two_by_two_section_edge(self) -> None:
        """Test that a cell on the right or bottom edge cannot have a corresponding two-by-two section"""
        right_edge_cell = self.get_cell()
        neighbor_cell_map = {
            Direction.LEFT_UP: self.get_cell(),
            Direction.UP: self.get_cell(),
            Direction.DOWN: self.get_cell(),
            Direction.LEFT_DOWN: self.get_cell(),
            Direction.LEFT: self.get_cell()
        }
        right_edge_cell.set_neighbor_map(neighbor_cell_map)
        with self.assertRaises(NonExistentNeighbor):
            right_edge_cell.get_two_by_two_section()

        bottom_edge_cell = self.get_cell()
        neighbor_cell_map = {
            Direction.LEFT_UP: self.get_cell(),
            Direction.UP: self.get_cell(),
            Direction.RIGHT_UP: self.get_cell(),
            Direction.RIGHT: self.get_cell(),
            Direction.LEFT: self.get_cell()
        }
        bottom_edge_cell.set_neighbor_map(neighbor_cell_map)
        with self.assertRaises(NonExistentNeighbor):
            bottom_edge_cell.get_two_by_two_section()
