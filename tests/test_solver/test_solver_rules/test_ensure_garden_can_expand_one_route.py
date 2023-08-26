from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.ensure_garden_can_expand_one_route import EnsureGardenCanExpandOneRoute, \
    NoPossibleSolutionFromCurrentState
from tests.build_board import build_board


class TestEnsureGardenCanExpandOneRoute(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """
        There are no gardens that need to expand via a single cell, so the board is not impacted by this solver rule.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            'O,3,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenCanExpandOneRoute(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_single_escape_route(self) -> None:
        """An undersized garden can only expand via a single cell, so this solver rule marks it as a non-wall cell."""
        board_details = [
            '_,_,_,_',
            '_,W,_,_',
            'O,3,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenCanExpandOneRoute(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,_',
            'O,W,_,_',
            'O,3,W,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_single_escape_route_for_garden_with_no_clue(self) -> None:
        """
        A garden that contains no clue can only expand via a single cell. Since every garden must contain one clue, this
        garden must expand via that cell, so this solver rule marks it as a non-wall cell.
        """
        board_details = [
            'O,O,W,_',
            'W,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenCanExpandOneRoute(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'O,O,W,_',
            'W,O,_,_',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_garden_with_multiple_clues(self) -> None:
        """If a garden contains more than one clue, the board is not in a solvable state, so an error is thrown."""
        board_details = [
            '1,O,3,W',
            'W,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentState):
            EnsureGardenCanExpandOneRoute(board).apply_rule()

    def test_non_naive_escape_route_for_garden_with_clue(self) -> None:
        """
        If a garden must expand through a specific cell in order to have space for the size of its clue,
        ideally that escape route cell would be marked as a non-wall. However, if the garden can still expand in other
        directions and is not immediately surrounded by adjacent cells that are all wall cells, this solver rule does
        not understand that the garden must extend through the escape route cell.

        For example, in the test below, the garden containing the clue in the bottom row must extend to the left
        in order to have space for 3 cells. However, since the cell immediately to the right of the clue cell on the
        bottom row is empty, this solver rule does not understand that the escape route cell must be a non-wall.
        """
        board_details = [
            '_,_,_,_',
            '_,_,W,W',
            '_,_,3,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenCanExpandOneRoute(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_non_naive_escape_route_for_garden_without_clue(self) -> None:
        """
        If a garden without a clue must expand through a specific cell in order to reach a clue cell, ideally that
        escape route cell would be marked as a non-wall. However, if the garden can still expand in other directions and
        is not immediately surrounded by adjacent cells that are all wall cells, this solver rule does not understand
        that the garden must extend through the escape route cell.

        For example, in the test below, the non-wall cell in the bottom row must extend to the left in order to connect
        to a clue cell. However, since the cell immediately to the right of the non-wall cell on the bottom row is
        empty, this solver rule does not understand that the escape route cell must be a non-wall.
        """
        board_details = [
            '_,_,_,_',
            '_,4,W,W',
            '_,_,O,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenCanExpandOneRoute(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_multiple_gardens_where_solver_rule_applies(self) -> None:
        """
        If there are multiple cells where this rule applies and should be marked as non-wall cells, it requires multiple
        iterations of this solver rule to mark all the cells as non-walls. Each iteration can only mark one cell as a
        non-wall. The reason for this is that once a cell is marked as a non-wall, the set of gardens can change.
        Therefore, the set of gardens be re-derived before potentially marking another cell as a non-wall.
        """
        board_details = [
            '_,_,_,_',
            '_,_,W,W',
            '_,_,_,3'
        ]
        board = self.create_board(board_details)
        ensure_garden_can_expand_solver_rule = EnsureGardenCanExpandOneRoute(board)

        # First iteration of the solver rule should only change one cell
        cell_changes = ensure_garden_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state1 = [
            '_,_,_,_',
            '_,_,W,W',
            '_,_,O,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state1)

        # Second iteration of the solver rule should also change one cell
        cell_changes = ensure_garden_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state2 = [
            '_,_,_,_',
            '_,_,W,W',
            '_,O,O,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)

        # On the third iteration, there are no more cells to apply this solver rule to, so the board is unchanged
        cell_changes = ensure_garden_can_expand_solver_rule.apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)
