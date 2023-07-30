from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board, AdjacentCluesError
from nurikabe.cell_state import CellState
from nurikabe.cell_group import CellGroup


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


class TestBoardSetup(TestBoard):
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


class TestBoardAsSimpleStringList(TestBoard):
    def setUp(self) -> None:
        level_details = [
            ',,,2',
            ',1,,',
            ',,,'
        ]
        self.board = self.create_board(level_details)

    def test_initial_setup(self) -> None:
        expected_simple_string_list = [
            '_,_,_,2',
            '_,1,_,_',
            '_,_,_,_'
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_simple_string_list)

    def test_after_cell_changes(self) -> None:
        self.board.get_cell_from_grid(row_number=0, col_number=1).update_cell_state(CellState.WALL)
        self.board.get_cell_from_grid(row_number=0, col_number=2).update_cell_state(CellState.WALL)
        self.board.get_cell_from_grid(row_number=1, col_number=3).update_cell_state(CellState.NON_WALL)
        self.board.get_cell_from_grid(row_number=2, col_number=3).update_cell_state(CellState.WALL)
        expected_simple_string_list = [
            '_,X,X,2',
            '_,1,_,O',
            '_,_,_,X'
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_simple_string_list)


class TestTwoByTwoWall(TestBoard):
    def setUp(self) -> None:
        level_details = [
            '1,,,',
            ',,,',
            ',3,,'
        ]
        self.board = self.create_board(level_details)

    def test_has_two_by_two_wall(self) -> None:
        # The board starts off with no wall cells, so there is of course no two-by-two section of walls
        self.assertFalse(self.board.has_two_by_two_wall())

        # These 4 cells form a two-by-two section
        two_by_two_cell_list = [
            self.board.get_cell_from_grid(row_number=0, col_number=1),
            self.board.get_cell_from_grid(row_number=0, col_number=2),
            self.board.get_cell_from_grid(row_number=1, col_number=1),
            self.board.get_cell_from_grid(row_number=1, col_number=2)
        ]

        # Set 3 of the above cells as walls
        for cell in two_by_two_cell_list[:3]:
            cell.update_cell_state(CellState.WALL)

        expected_board_state = [
            '1,X,X,_',
            '_,X,_,_',
            '_,3,_,_'
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)

        # There is still no two-by-two section of walls
        self.assertFalse(self.board.has_two_by_two_wall())

        # Set the last of the 4 above cells as a wall
        two_by_two_cell_list[3].update_cell_state(CellState.WALL)

        expected_board_state = [
            '1,X,X,_',
            '_,X,X,_',
            '_,3,_,_'
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)

        # Now all 4 cells in that two-by-two section are walls
        self.assertTrue(self.board.has_two_by_two_wall())


class TestCellGroups(TestBoard):
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

        expected_board_state = [
            '_,O,_,_,_,_',
            '_,1,O,_,_,_',
            'O,_,_,_,_,_'
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
            'O,O,_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

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

        expected_board_state = [
            '_,_,_,_,X,_',
            '_,1,_,_,X,_',
            '_,_,_,_,_,X'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

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

    def test_get_wall_section(self) -> None:
        level_details = [
            ',,,,,',
            ',1,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)

        # Mark some cells as walls
        wall_cells = [
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=5),
            board.get_cell_from_grid(row_number=2, col_number=3)  # This one is not adjacent to the others
        ]
        for wall_cell in wall_cells:
            wall_cell.update_cell_state(CellState.WALL)

        expected_board_state = [
            '_,_,_,_,X,_',
            '_,1,_,_,X,X',
            '_,_,_,X,_,_'
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
            '_,_,_,_,X,_',
            '_,1,_,X,X,X',
            '_,_,_,X,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertEqual(len(board.get_all_wall_sections()), 1)

    def test_cell_group_get_adjacent_neighbors(self) -> None:
        level_details = [
            ',,,,,',
            ',1,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)
        cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2)
        })
        adjacent_neighbor_cells = cell_group.get_adjacent_neighbors()
        expected_adjacent_neighbors = {
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2)
        }
        self.assertEqual(adjacent_neighbor_cells, expected_adjacent_neighbors)

    def test_is_garden_fully_enclosed(self) -> None:
        level_details = [
            ',,,2,,',
            ',5,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)

        clue_cell = board.get_cell_from_grid(row_number=0, col_number=3)

        # Set one cell next to the clue cell as a non-wall to make it a part of the garden
        board.get_cell_from_grid(row_number=0, col_number=4).update_cell_state(CellState.NON_WALL)

        wall_cells = [
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=4),
        ]

        # At first, the garden is not fully enclosed
        expected_board_state = [
            '_,_,_,2,O,_',
            '_,5,_,_,_,_',
            '_,_,_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        # Mark the cell to the left and the cell to the right as walls
        wall_cells[0].update_cell_state(CellState.WALL)
        wall_cells[1].update_cell_state(CellState.WALL)

        # The garden is still not fully enclosed
        expected_board_state = [
            '_,_,X,2,O,X',
            '_,5,_,_,_,_',
            '_,_,_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        # Mark one of the cells just below the garden as a wall
        wall_cells[2].update_cell_state(CellState.WALL)

        # The garden is still not fully enclosed
        expected_board_state = [
            '_,_,X,2,O,X',
            '_,5,_,X,_,_',
            '_,_,_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertFalse(board.get_garden(clue_cell).is_garden_fully_enclosed())

        # Mark the other cell just below the garden as a wall
        wall_cells[3].update_cell_state(CellState.WALL)

        # Now the garden should be fully enclosed
        expected_board_state = [
            '_,_,X,2,O,X',
            '_,5,_,X,X,_',
            '_,_,_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
        self.assertTrue(board.get_garden(clue_cell).is_garden_fully_enclosed())
