from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.separate_gardens_with_clues import SeparateGardensWithClues
from tests.build_board import build_board


class TestSeparateGardensWithClues(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_close_gardens(self) -> None:
        """If there are no gardens with common adjacent cells, this solver rule should have no impact."""
        board_details = [
            '_,_,_,3',
            '_,4,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateGardensWithClues(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_separate_clues(self) -> None:
        """Gardens that are just a single clue cell should be separated by wall cell."""
        board_details = [
            '_,_,3,_',
            '_,4,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateGardensWithClues(board).apply_rule()

        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,X,3,_',
            '_,4,X,_',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_separate_gardens_with_clues(self) -> None:
        """This solver rule should separate gardens that have clues."""
        board_details = [
            '_,_,_,3',
            '_,4,_,O',
            '_,O,O,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateGardensWithClues(board).apply_rule()

        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,3',
            '_,4,X,O',
            '_,O,O,X'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_dont_separate_gardens_without_clue(self) -> None:
        """
        If a garden does not have a clue, it may really be part of a different garden, so don't separate them with
        wall cells.
        """
        board_details = [
            '_,_,_,O',
            '_,4,_,O',
            '_,O,O,_'
        ]
        board = self.create_board(board_details)
        cell_changes = SeparateGardensWithClues(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)
