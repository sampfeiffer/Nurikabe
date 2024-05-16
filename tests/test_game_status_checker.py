from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.cell_group import MultipleCluesInCellGroupError, NoCluesInCellGroupError
from nurikabe.cell_state import CellState
from nurikabe.game_status_checker import GameStatusChecker
from nurikabe.level import LevelBuilderFromStringList


class TestGameStatusChecker(TestCase):
    screen = MagicMock(name='Screen')
    level = LevelBuilderFromStringList(level_details=[
        '1,,,',
        ',,,',
        ',3,,',
    ]).build_level()

    def setUp(self) -> None:
        self.board = Board(self.level, self.screen)
        self.game_status_checker = GameStatusChecker(self.board)

    def test_has_expected_number_of_weak_garden_cells(self) -> None:
        # We expect 4 weak garden cells since the sum of the clues is 4
        self.assertEqual(self.game_status_checker.get_expected_number_of_weak_garden_cells(), 4)

        # We expect 4 weak garden cells, but all 12 cells are weak garden cells
        self.assertFalse(self.game_status_checker.has_expected_number_of_weak_garden_cells())

        # Set 8 empty cells as walls
        weak_garden_cell_list = list(self.board.get_weak_garden_cells())
        for cell in weak_garden_cell_list[:8]:
            cell.update_cell_state(CellState.WALL)

        # Now we should only have 4 weak garden cells
        self.assertTrue(self.game_status_checker.has_expected_number_of_weak_garden_cells())

        # It does not matter if the remaining two non clue cells are set as non-walls or left empty. Both are considered
        # weak garden cells. Cells do not need to be marked as non-walls for the board to be considered solved. It is
        # only required that wall cells are marked as walls.
        for cell in weak_garden_cell_list[-2:]:
            cell.update_cell_state(CellState.NON_WALL)
        self.assertTrue(self.game_status_checker.has_expected_number_of_weak_garden_cells())

    def test_are_all_walls_connected(self) -> None:
        # The board starts off with no wall cells, so the (non-existent) wall cells are trivially all connected
        self.assertTrue(self.game_status_checker.are_all_walls_connected())

        # Set one cell as a wall. Since it's the only wall cell, all wall cells are connected.
        self.board.get_cell_from_grid(row_number=0, col_number=1).update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,_,_,_',
            '_,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        self.assertTrue(self.game_status_checker.are_all_walls_connected())

        # Set another adjacent cell as a wall. All wall cells are still connected.
        self.board.get_cell_from_grid(row_number=1, col_number=1).update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            '_,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        self.assertTrue(self.game_status_checker.are_all_walls_connected())

        # Set a non-adjacent cell as a wall. Now there are two separate sections of wall cells that are not connected.
        self.board.get_cell_from_grid(row_number=2, col_number=2).update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            '_,3,W,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        self.assertFalse(self.game_status_checker.are_all_walls_connected())

        # Set another cell as a wall such that the new wall cell connects the two disjoint wall sections into one wall
        # section.
        self.board.get_cell_from_grid(row_number=1, col_number=2).update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,W,_',
            '_,3,W,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        self.assertTrue(self.game_status_checker.are_all_walls_connected())

    def test_do_all_weak_gardens_have_exactly_one_clue(self) -> None:
        # The board starts off with two clues. Since there are no wall cells, all cells, including the two clue cells
        # are part of the same weak garden
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertEqual(len(weak_gardens), 1)
        self.assertFalse(self.game_status_checker.do_all_weak_gardens_have_exactly_one_clue(weak_gardens))

        cell_list = [
            self.board.get_cell_from_grid(row_number=0, col_number=1),
            self.board.get_cell_from_grid(row_number=1, col_number=1),
            self.board.get_cell_from_grid(row_number=2, col_number=0),
        ]

        # Set some cells as walls. Since they don't completely disconnect the two clue cells, the clue cells are still
        # part of the same weak garden.
        for cell in cell_list[:2]:
            cell.update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            '_,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertEqual(len(weak_gardens), 1)
        self.assertFalse(self.game_status_checker.do_all_weak_gardens_have_exactly_one_clue(weak_gardens))

        # Set another cell as a wall. Now the two clue cells are completely separated into two distinct weak gardens
        cell_list[2].update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            'W,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertEqual(len(weak_gardens), 2)
        self.assertTrue(self.game_status_checker.do_all_weak_gardens_have_exactly_one_clue(weak_gardens))

        # Set that last cell as a non-wall and now the clue cells are once again part of the same weak garden
        cell_list[2].update_cell_state(CellState.NON_WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            'O,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertEqual(len(weak_gardens), 1)
        self.assertFalse(self.game_status_checker.do_all_weak_gardens_have_exactly_one_clue(weak_gardens))

    def test_are_all_weak_gardens_correct_size(self) -> None:
        # In order to test if a weak garden is the correct size, there must be exactly one clue per garden. Since the
        # board starts with as one weak garden containing two clues, we expect an error to be thrown in this calc.
        weak_gardens = self.board.get_all_weak_gardens()
        with self.assertRaises(MultipleCluesInCellGroupError):
            self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens)

        # Set some cells as walls so that the clue cells are split into two distinct weak gardens
        cell_list1 = [
            self.board.get_cell_from_grid(row_number=0, col_number=1),
            self.board.get_cell_from_grid(row_number=1, col_number=1),
            self.board.get_cell_from_grid(row_number=2, col_number=0),
        ]
        for cell in cell_list1:
            cell.update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,_,_',
            '_,W,_,_',
            'W,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()

        # Since each weak garden only has one clue, the check can be run. However, the weak gardens are not the right
        # size.
        self.assertFalse(self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens))

        # Set some more wall cells so that one of the weak gardens is the correct size but the other is not
        cell_list2 = [
            self.board.get_cell_from_grid(row_number=0, col_number=2),
            self.board.get_cell_from_grid(row_number=0, col_number=3),
            self.board.get_cell_from_grid(row_number=1, col_number=2),
            self.board.get_cell_from_grid(row_number=1, col_number=3),
        ]
        for cell in cell_list2:
            cell.update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,W,W',
            '_,W,W,W',
            'W,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()

        # Since one of the weak gardens is not the correct size, we expect this to be False
        self.assertFalse(self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens))

        # Set another cell as a wall in a way that makes both weak gardens the correct size
        self.board.get_cell_from_grid(row_number=1, col_number=0).update_cell_state(CellState.WALL)
        expected_board_state = [
            '1,W,W,W',
            'W,W,W,W',
            'W,3,_,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertTrue(self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens))

        # Set one of the empty cells as a non-wall cell. This has no impact since cells do not need to be marked as
        # non-walls for the board to be considered solved. It is only required that wall cells are marked as walls.
        self.board.get_cell_from_grid(row_number=2, col_number=2).update_cell_state(CellState.NON_WALL)
        expected_board_state = [
            '1,W,W,W',
            'W,W,W,W',
            'W,3,O,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)
        weak_gardens = self.board.get_all_weak_gardens()
        self.assertTrue(self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens))

        # Set a cell as empty so that there is a weak garden with no clue
        self.board.get_cell_from_grid(row_number=0, col_number=3).update_cell_state(CellState.EMPTY)
        expected_board_state = [
            '1,W,W,_',
            'W,W,W,W',
            'W,3,O,_',
        ]
        self.assertEqual(self.board.as_simple_string_list(), expected_board_state)

        # Since this new weak garden has no clue, we cannot determine if it's the right size, so we expect an error.
        # Note that this error is only guaranteed to be thrown if all other weak gardens are determined to be the right
        # size due to Python short-circuiting the all() operator.
        weak_gardens = self.board.get_all_weak_gardens()
        with self.assertRaises(NoCluesInCellGroupError):
            self.game_status_checker.are_all_weak_gardens_correct_size(weak_gardens)
