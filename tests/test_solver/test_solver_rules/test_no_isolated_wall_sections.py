from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.board_state_checker import NoPossibleSolutionFromCurrentStateError
from nurikabe.solver.solver_rules.no_isolated_wall_sections import NoIsolatedWallSections
from tests.build_board import build_board


class TestNoIsolatedWallSections(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """
        If there are no cells that provide the only escape route for a wall section, then this solver rule should not
        trigger any cell changes.
        """
        board_details = [
            '1,_,_,W',
            '_,_,_,_',
            '_,3,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_no_escape_route_for_only_wall_section(self) -> None:
        """
        If a wall section has no empty adjacent cells but there are no other wall sections that it needs to connect to,
        then this solver rule should not trigger any cell changes nor throw any errors.
        """
        board_details = [
            '_,_,_,_',
            'O,O,_,_',
            'W,W,O,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_no_escape_route_with_multiple_wall_sections(self) -> None:
        """
        If a wall section has no empty adjacent cells and there are other wall sections that it needs to connect to,
        then the board is in a bad state and an error should be thrown.
        """
        board_details = [
            '_,_,_,W',
            'O,O,_,_',
            'W,W,O,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            NoIsolatedWallSections(board).apply_rule()

    def test_only_escape_route_for_only_wall_section(self) -> None:
        """
        If there are is a cell that provides the only escape route for a wall section, but there are no other wall
        sections to connect to, then this solver rule should not trigger any cell changes.
        """
        board_details = [
            '1,_,_,_',
            '_,_,O,_',
            '_,_,W,3',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_only_escape_route_with_multiple_wall_sections(self) -> None:
        """
        If there are is a cell that provides the only escape route for a wall section, and there are other wall
        sections to connect to, then the escape route cell should be marked as a wall.
        """
        board_details = [
            '1,_,_,_',
            'W,_,O,_',
            '_,_,W,3',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '1,_,_,_',
            'W,_,O,_',
            '_,W,W,3',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_naive_escape_route(self) -> None:
        """
        If a wall section must extend through a specific cell to connect to the other wall sections even if there are
        other cells adjacent to the wall section that are empty since those other empty cells are not useful for
        connecting to the other wall sections.
        """
        board_details = [
            'W,_,_,_',
            '_,_,O,O',
            '_,_,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'W,_,_,_',
            '_,_,O,O',
            '_,W,W,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_multiple_cells_in_only_escape_route(self) -> None:
        """
        If the wall section must extend through multiple cells that make up the escape route, it does not require
        multiple iterations of this solver rule to mark all the escape route cells as walls. A single iteration can
        mark all the escape route cells as walls.
        """
        board_details = [
            '_,W,_,_',
            '_,_,O,O',
            '_,_,_,W',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,W,_,_',
            '_,_,O,O',
            '_,W,W,W',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_multiple_escape_routes(self) -> None:
        """
        The wall sections can connect via multiple routes. There are no cells that are critical to connecting the wall
        sections. Therefore, this solver rule should not trigger any cell changes.
        """
        board_details = [
            '_,W,_',
            '_,_,O',
            'W,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)
