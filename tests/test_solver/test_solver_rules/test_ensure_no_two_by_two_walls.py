from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.ensure_no_two_by_two_walls import EnsureNoTwoByTwoWalls
from tests.build_board import build_board


class TestEnsureNoTwoByTwoWalls(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """There are no cells that need to be marked as a non-wall to avoid a two-by-two wall section."""
        board_details = [
            'X,_,_,_',
            '_,X,X,_',
            '_,O,X,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureNoTwoByTwoWalls(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_prevent_two_by_two_walls(self) -> None:
        """There are cells that need to be marked as a non-wall to avoid a two-by-two wall section."""
        board_details = [
            '_,X,_,_',
            'X,X,X,X',
            '_,_,X,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureNoTwoByTwoWalls(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'O,X,O,_',
            'X,X,X,X',
            '_,O,X,O'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
