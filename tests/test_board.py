from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board, AdjacentCluesError
from nurikabe.cell_state import CellState


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    @staticmethod
    def create_level_from_string_list(level_details: list[str]) -> Level:
        return LevelBuilderFromStringList(level_details).build_level()

    def create_board(self, level_details: list[str]) -> Board:
        level = self.create_level_from_string_list(level_details)
        return Board(level, self.screen)

    def test_vertically_adjacent_clues(self) -> None:
        level_details = [
            '1,',
            '1,',
        ]
        with self.assertRaises(AdjacentCluesError):
            self.create_board(level_details)

    def test_horizontally_adjacent_clues(self) -> None:
        level_details = [
            ',',
            '1,1',
        ]
        with self.assertRaises(AdjacentCluesError):
            self.create_board(level_details)

    def test_cell_neighbor_count(self) -> None:
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)

        corner_cells = (
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=3)
        )
        for corner_cell in corner_cells:
            self.assertEqual(len(corner_cell.neighbor_cell_map), 3)

        edge_cells = (
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2)
        )
        for edge_cell in edge_cells:
            self.assertEqual(len(edge_cell.neighbor_cell_map), 5)

        center_cells = (
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2)
        )
        for center_cell in center_cells:
            self.assertEqual(len(center_cell.neighbor_cell_map), 8)

    def test_get_garden(self) -> None:
        level_details = [
            ',,,,,',
            ',1,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)

        clue_cell = board.get_cell_from_grid(row_number=1, col_number=1)

        # Find the garden starting with the clue cell. Since there are no attached non-wall cells, the garden should
        # just contain the clue cell
        self.assertEqual(board.get_garden(clue_cell).cells, {clue_cell})

        # Mark two adjacent cells and one diagonally adjacent cell as non-walls. We only expect the adjacent cells to
        # be a part of the garden
        adjacent_cell1 = board.get_cell_from_grid(row_number=0, col_number=1)
        adjacent_cell1.update_cell_state(CellState.NON_WALL)

        adjacent_cell2 = board.get_cell_from_grid(row_number=1, col_number=2)
        adjacent_cell2.update_cell_state(CellState.NON_WALL)

        diagonal_cell = board.get_cell_from_grid(row_number=2, col_number=0)
        diagonal_cell.update_cell_state(CellState.NON_WALL)

        # Check that the garden contains the correct cells
        self.assertEqual(board.get_garden(clue_cell).cells, {clue_cell, adjacent_cell1, adjacent_cell2})

        # Now mark another cell as adjacent causing the diagonal cell to be vertically/horizontally connected to the
        # garden
        adjacent_cell3 = board.get_cell_from_grid(row_number=2, col_number=1)
        adjacent_cell3.update_cell_state(CellState.NON_WALL)

        # Check that the garden contains the all 5 cells
        self.assertEqual(board.get_garden(clue_cell).cells,
                         {clue_cell, adjacent_cell1, adjacent_cell2, diagonal_cell, adjacent_cell3})

        # It shouldn't matter which cell is considered the "root" of the garden
        self.assertEqual(board.get_garden(diagonal_cell).cells, board.get_garden(clue_cell).cells)

    def test_get_all_weak_gardens(self) -> None:
        level_details = [
            ',,,,,',
            ',1,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)

        # There should only be one weak garden containing all cells in board
        all_weak_gardens = board.get_all_weak_gardens()
        self.assertEqual(len(all_weak_gardens), 1)
        self.assertEqual(list(all_weak_gardens)[0].cells, set(board.flat_cell_list))

        # Corner off some cells
        wall_cells = {
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=4),
            board.get_cell_from_grid(row_number=2, col_number=5)
        }
        for wall_cell in wall_cells:
            wall_cell.update_cell_state(CellState.WALL)

        # There should now be two weak gardens
        all_weak_gardens = board.get_all_weak_gardens()
        self.assertEqual(len(all_weak_gardens), 2)
        weak_garden1 = {
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=1, col_number=5)
        }
        weak_garden2 = set(board.flat_cell_list) - wall_cells.union(weak_garden1)

        for weak_garden in all_weak_gardens:
            weak_garden_cells = weak_garden.cells
            if len(weak_garden_cells) == 2:
                self.assertEqual(weak_garden_cells, weak_garden1)
            elif len(weak_garden_cells) == 13:
                self.assertEqual(weak_garden_cells, weak_garden2)
            else:
                raise RuntimeError('Unexpected weak garden size')
