from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.naively_unreachable_from_garden import NaivelyUnreachableFromGarden
from tests.build_board import build_board


class TestNaivelyUnreachableFromGarden(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_all_cells_manhattan_reachable(self) -> None:
        """A cells are Manhattan reachable from a garden, so the board is not impacted by this solver rule."""
        board_details = [
            '_,_,_,_,_,_',
            '_,4,_,_,3,O',
            '_,_,_,_,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NaivelyUnreachableFromGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_manhattan_reachable_through_walls(self) -> None:
        """
        This solver rule is a naive (and therefore computationally cheap) reachability check. It does not check if there
        are walls in the way when determining if a cell is reachable by a garden.
        """
        board_details = [
            '_,O,W,_',
            '_,4,W,_',
            '_,_,W,W',
        ]
        board = self.create_board(board_details)
        cell_changes = NaivelyUnreachableFromGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_unreachable_cells_from_clue(self) -> None:
        """Empty cells that are Manhattan unreachable from a garden are marked as walls."""
        board_details = [
            '_,_,_,_,_',
            '_,4,_,_,_',
            '_,O,_,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NaivelyUnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,W,W',
            '_,4,_,_,W',
            '_,O,_,_,W',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_wall_cells_not_impacted(self) -> None:
        """
        This solver rule only impacts empty cells. Cells that are (incorrectly) marked as non-walls are not impacted.
        """
        board_details = [
            '_,_,_,_,O',
            '_,4,_,_,O',
            '_,O,_,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = NaivelyUnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,W,O',
            '_,4,_,_,O',
            '_,O,_,_,W',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)
