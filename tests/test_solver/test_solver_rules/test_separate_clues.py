from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.separate_clues import SeparateClues
from tests.build_board import build_board


class TestSeparateClues(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """Ensure that when there are no clues to separate, the board state is not impacted by this solver rule."""
        board_details = [
            '1,_,_,_',
            '_,_,_,_',
            '_,3,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateClues(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_separate_clues(self) -> None:
        """Cells that are adjacent to two clues should be marked as walls."""
        board_details = [
            '1,_,3,_',
            '_,_,_,2',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateClues(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '1,W,3,W',
            '_,_,W,2',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_separate_three_clues(self) -> None:
        """Cells that are adjacent to more than two clues should also be marked as walls."""
        board_details = [
            '1,_,3,_',
            '_,2,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateClues(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '1,W,3,_',
            'W,2,W,_',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_clues_already_separated(self) -> None:
        """
        If cells that are adjacent to more than one clue are already marked as walls, then this solver rule has no
        impact.
        """
        board_details = [
            '1,W,3,_',
            'W,2,W,_',
            '_,W,1,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateClues(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)
