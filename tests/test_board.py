from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import AdjacentCluesError, Board
from nurikabe.cell_group import CellGroup
from nurikabe.cell_state import CellState
from nurikabe.level import BadLevelSetupError
from tests.build_board import build_board


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)


class TestBoardSetup(TestBoard):
    def test_vertically_adjacent_clues(self) -> None:
        board_details = [
            '1,_',
            '1,_',
        ]
        with self.assertRaises(AdjacentCluesError):
            self.create_board(board_details)

    def test_horizontally_adjacent_clues(self) -> None:
        board_details = [
            '_,_',
            '1,1',
        ]
        with self.assertRaises(AdjacentCluesError):
            self.create_board(board_details)

    def test_cell_neighbor_count(self) -> None:
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)

        corner_cells = (
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=3),
        )
        for corner_cell in corner_cells:
            self.assertEqual(len(corner_cell.neighbor_cell_map), 3)

        edge_cells = (
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2),
        )
        for edge_cell in edge_cells:
            self.assertEqual(len(edge_cell.neighbor_cell_map), 5)

        center_cells = (
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
        )
        for center_cell in center_cells:
            self.assertEqual(len(center_cell.neighbor_cell_map), 8)


class TestBoardAsSimpleStringList(TestBoard):
    def test_initial_setup(self) -> None:
        board_details = [
            '_,_,_,2',
            '_,1,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        expected_simple_string_list = [
            '_,_,_,2',
            '_,1,_,_',
            '_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_simple_string_list)

    def test_after_cell_changes(self) -> None:
        board_details = [
            '_,_,_,2',
            '_,1,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)

        board.get_cell_from_grid(row_number=0, col_number=1).update_cell_state(CellState.WALL)
        board.get_cell_from_grid(row_number=0, col_number=2).update_cell_state(CellState.WALL)
        board.get_cell_from_grid(row_number=1, col_number=3).update_cell_state(CellState.NON_WALL)
        board.get_cell_from_grid(row_number=2, col_number=3).update_cell_state(CellState.WALL)
        expected_simple_string_list = [
            '_,W,W,2',
            '_,1,_,O',
            '_,_,_,W',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_simple_string_list)

    def test_build_board_with_cell_states(self) -> None:
        board_details = [
            '_,_,W,2',
            'W,1,O,_',
            'O,_,_,_',
        ]
        board = self.create_board(board_details)

        cell_state_matrix = [[cell.cell_state for cell in row] for row in board.cell_grid]

        expected_cell_state_matrix = [
            [CellState.EMPTY, CellState.EMPTY, CellState.WALL, CellState.CLUE],
            [CellState.WALL, CellState.CLUE, CellState.NON_WALL, CellState.EMPTY],
            [CellState.NON_WALL, CellState.EMPTY, CellState.EMPTY, CellState.EMPTY],
        ]

        self.assertEqual(cell_state_matrix, expected_cell_state_matrix)

    def test_build_board_with_bad_char(self) -> None:
        """If there is an unexpected character in the board details, an error should be thrown."""
        board_details = [
            '_,_,W,2',
            'W,1,O,e',
            'O,_,_,_',
        ]
        with self.assertRaises(BadLevelSetupError):
            self.create_board(board_details)


class TestTwoByTwoWall(TestBoard):
    def test_fresh_board_has_no_two_by_two_walls(self) -> None:
        board_details = [
            '1,_,_,_',
            '_,_,_,_',
            '_,3,_,_',
        ]
        board = self.create_board(board_details)

        # The board starts off with no wall cells, so there is of course no two-by-two section of walls
        self.assertFalse(board.has_two_by_two_wall())

    def test_board_has_three_of_four_walls(self) -> None:
        board_details = [
            '1,W,W,_',
            '_,W,_,_',
            '_,3,_,_',
        ]
        board = self.create_board(board_details)
        self.assertFalse(board.has_two_by_two_wall())

    def test_board_has_two_by_two_walls(self) -> None:
        board_details = [
            '1,W,W,_',
            '_,W,W,_',
            '_,3,_,_',
        ]
        board = self.create_board(board_details)
        self.assertTrue(board.has_two_by_two_wall())


class TestCellGroups(TestBoard):
    def test_get_garden(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,1,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)

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

        expected_board_state = [
            '_,O,_,_,_,_',
            '_,1,O,_,_,_',
            'O,_,_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

        # Check that the garden contains the correct cells
        self.assertEqual(board.get_garden(clue_cell).cells, {clue_cell, adjacent_cell1, adjacent_cell2})

        # Now mark another cell as adjacent causing the diagonal cell to be vertically/horizontally connected to the
        # garden
        adjacent_cell3 = board.get_cell_from_grid(row_number=2, col_number=1)
        adjacent_cell3.update_cell_state(CellState.NON_WALL)

        expected_board_state = [
            '_,O,_,_,_,_',
            '_,1,O,_,_,_',
            'O,O,_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

        # Check that the garden contains the all 5 cells
        self.assertEqual(board.get_garden(clue_cell).cells,
                         {clue_cell, adjacent_cell1, adjacent_cell2, diagonal_cell, adjacent_cell3})

        # It shouldn't matter which cell is considered the "root" of the garden
        self.assertEqual(board.get_garden(diagonal_cell).cells, board.get_garden(clue_cell).cells)

    def test_get_all_weak_gardens(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,1,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)

        # There should only be one weak garden containing all cells in board
        all_weak_gardens = board.get_all_weak_gardens()
        self.assertEqual(len(all_weak_gardens), 1)
        self.assertEqual(next(iter(all_weak_gardens)).cells, set(board.flat_cell_list))

        # Corner off some cells
        wall_cells = {
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=4),
            board.get_cell_from_grid(row_number=2, col_number=5),
        }
        for wall_cell in wall_cells:
            wall_cell.update_cell_state(CellState.WALL)

        expected_board_state = [
            '_,_,_,_,W,_',
            '_,1,_,_,W,_',
            '_,_,_,_,_,W',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

        # There should now be two weak gardens
        all_weak_gardens = board.get_all_weak_gardens()
        self.assertEqual(len(all_weak_gardens), 2)
        weak_garden1 = {
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=1, col_number=5),
        }
        weak_garden2 = set(board.flat_cell_list) - wall_cells.union(weak_garden1)

        for weak_garden in all_weak_gardens:
            weak_garden_cells = weak_garden.cells
            if len(weak_garden_cells) == 2:  # noqa: PLR2004
                self.assertEqual(weak_garden_cells, weak_garden1)
            elif len(weak_garden_cells) == 13:  # noqa: PLR2004
                self.assertEqual(weak_garden_cells, weak_garden2)
            else:
                msg = 'Unexpected weak garden size'
                raise RuntimeError(msg)

    def test_get_wall_section(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,1,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)

        # Mark some cells as walls
        wall_cells = [
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=5),
            board.get_cell_from_grid(row_number=2, col_number=3),  # This one is not adjacent to the others
        ]
        for wall_cell in wall_cells:
            wall_cell.update_cell_state(CellState.WALL)

        expected_board_state = [
            '_,_,_,_,W,_',
            '_,1,_,_,W,W',
            '_,_,_,W,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

        # Check that the wall section starting with the first wall cell contains the first 3 wall cells since they are
        # connected
        self.assertEqual(board.get_wall_section(wall_cells[0]).cells, set(wall_cells[:3]))

        # Check there are two distinct wall sections
        self.assertEqual(len(board.get_all_wall_sections()), 2)

        # Now we connect those two wall sections via another wall, and they are merged into one large wall section
        board.get_cell_from_grid(row_number=1, col_number=3).update_cell_state(CellState.WALL)
        expected_board_state = [
            '_,_,_,_,W,_',
            '_,1,_,W,W,W',
            '_,_,_,W,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertEqual(len(board.get_all_wall_sections()), 1)

    def test_cell_group_get_adjacent_neighbors(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,1,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)
        cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
        })
        adjacent_neighbor_cells = cell_group.get_adjacent_neighbors()
        expected_adjacent_neighbors = {
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2),
        }
        self.assertEqual(adjacent_neighbor_cells, expected_adjacent_neighbors)

    def test_is_garden_fully_enclosed(self) -> None:
        board_details = [
            '_,_,_,2,O,_',
            '_,5,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)

        clue_cell = board.get_cell_from_grid(row_number=0, col_number=3)

        # At first, the garden is not fully enclosed
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        wall_cells = [
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=4),
        ]

        # Mark the cell to the left and the cell to the right as walls
        wall_cells[0].update_cell_state(CellState.WALL)
        wall_cells[1].update_cell_state(CellState.WALL)

        # The garden is still not fully enclosed
        expected_board_state = [
            '_,_,W,2,O,W',
            '_,5,_,_,_,_',
            '_,_,_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        # Mark one of the cells just below the garden as a wall
        wall_cells[2].update_cell_state(CellState.WALL)

        # The garden is still not fully enclosed
        expected_board_state = [
            '_,_,W,2,O,W',
            '_,5,_,W,_,_',
            '_,_,_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        # Mark the other cell just below the garden as a wall
        wall_cells[3].update_cell_state(CellState.WALL)

        # Now the garden should be fully enclosed
        expected_board_state = [
            '_,_,W,2,O,W',
            '_,5,_,W,W,_',
            '_,_,_,_,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertTrue(board.get_garden(clue_cell).is_garden_fully_enclosed())
