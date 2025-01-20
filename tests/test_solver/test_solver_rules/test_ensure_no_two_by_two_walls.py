from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.board_state_checker import NoPossibleSolutionFromCurrentStateError
from nurikabe.solver.solver_rules.ensure_no_two_by_two_walls import EnsureNoTwoByTwoWalls
from tests.build_board import build_board


class TestEnsureNoTwoByTwoWalls(TestCase):
    screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """There are no cells that need to be marked as a non-wall to avoid a two-by-two wall section."""
        board_details = [
            'W,_,_,_',
            '_,W,W,_',
            '_,O,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureNoTwoByTwoWalls(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_prevent_two_by_two_walls(self) -> None:
        """There are cells that need to be marked as a non-wall to avoid a two-by-two wall section."""
        board_details = [
            '_,W,_,_',
            'W,W,W,W',
            '_,_,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureNoTwoByTwoWalls(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'O,W,O,_',
            'W,W,W,W',
            '_,O,W,O',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_has_two_by_two_walls(self) -> None:
        """
        If there is already a two-by-two section of walls, the board is not in a solvable state, so an error is thrown.
        """
        board_details = [
            '_,W,W,_',
            'W,W,W,W',
            '_,_,W,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EnsureNoTwoByTwoWalls(board).apply_rule()
