from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.fill_correctly_sized_weak_garden import FillCorrectlySizedWeakGarden
from tests.build_board import build_board


class TestFillCorrectlySizedWeakGarden(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_correctly_sized_weak_garden(self) -> None:
        """If there is a correctly sized weak garden, mark the empty cells as non-walls."""
        board_details = [
            '_,W,_,3',
            '_,_,W,_',
            '_,_,_,W'
        ]
        board = self.create_board(board_details)
        cell_changes = FillCorrectlySizedWeakGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,W,O,3',
            '_,_,W,O',
            '_,_,_,W'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_too_small_weak_garden(self) -> None:
        """If there is a weak garden that is (incorrectly) too small, it should not be impacted by this solver rule."""
        board_details = [
            '_,W,_,3',
            '_,_,W,W',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = FillCorrectlySizedWeakGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_too_large_weak_garden(self) -> None:
        """If there is a weak garden that is too large, it should not be impacted by this solver rule."""
        board_details = [
            '_,W,_,3',
            '_,_,W,_',
            '_,_,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = FillCorrectlySizedWeakGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_weak_garden_with_no_clue(self) -> None:
        """If there is a weak garden that has no clue cell, it should not be impacted by this solver rule."""
        board_details = [
            '_,W,_,_',
            '_,_,W,_',
            '_,_,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = FillCorrectlySizedWeakGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_weak_garden_with_multiple_clues(self) -> None:
        """If there is a weak garden that has multiple clue cells, it should not be impacted by this solver rule."""
        board_details = [
            '_,W,2,_',
            '_,W,_,_',
            '_,_,W,2'
        ]
        board = self.create_board(board_details)
        cell_changes = FillCorrectlySizedWeakGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)
