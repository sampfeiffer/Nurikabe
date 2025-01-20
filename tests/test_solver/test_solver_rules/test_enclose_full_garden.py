from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.board_state_checker import NoPossibleSolutionFromCurrentStateError
from nurikabe.solver.solver_rules.enclose_full_garden import EncloseFullGarden
from tests.build_board import build_board


class TestEncloseFullGarden(TestCase):
    screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_full_gardens(self) -> None:
        """There are no full gardens that need to be enclosed, so the board is not impacted by this solver rule."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            'O,3,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EncloseFullGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_enclose_full_garden(self) -> None:
        """Gardens that have the correct number of cells are enclosed by walls."""
        board_details = [
            '_,_,_,1',
            '_,O,_,_',
            'O,3,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EncloseFullGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,W,W,1',
            'W,O,W,W',
            'O,3,W,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_dont_enclose_too_large_garden(self) -> None:
        """If a garden contains too many cells, don't enclose it with walls."""
        board_details = [
            '_,_,_,_',
            'O,O,_,_',
            'O,3,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EncloseFullGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_garden_with_multiple_clues(self) -> None:
        """If a garden contains more than one clue, the board is not in a solvable state, so an error is thrown."""
        board_details = [
            '1,O,3,W',
            'W,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EncloseFullGarden(board).apply_rule()
