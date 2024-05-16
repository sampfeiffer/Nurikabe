from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.ensure_garden_without_clue_can_expand import (
    EnsureGardenWithoutClueCanExpand,
    NoPossibleSolutionFromCurrentStateError,
)
from tests.build_board import build_board


class TestEnsureGardenWithoutClueCanExpand(TestCase):
    screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """
        There are no gardens without a clue that needs to expand via a single cell, so the board is not impacted by this
        solver rule.
        """
        board_details = [
            '_,_,_,_',
            '_,W,_,_',
            'O,3,W,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_no_cell_changes_due_to_two_available_gardens_with_clue(self) -> None:
        """
        A garden without a clue can expand in two different directions to connect to one of two gardens with a clue.
        There is no cell that if marked as a wall would block the garden without a clue from connecting with at least
        one garden with a clue. Therefore, the board is not impacted by this solver rule.
        """
        board_details = [
            '_,_,W,_,_',
            '4,_,O,_,4',
            '_,_,W,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_no_cell_changes_due_to_two_available_paths_to_garden_with_clue(self) -> None:
        """
        A garden without a clue can expand in two different directions to connect to a garden with a clue. There is no
        cell that if marked as a wall would block the garden without a clue from connecting to the garden with a clue.
        Therefore, the board is not impacted by this solver rule.
        """
        board_details = [
            '_,_,_',
            'O,W,5',
            '_,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_single_escape_route_for_garden(self) -> None:
        """
        A garden that contains no clue can only expand via a single cell. Since every garden must contain one clue, this
        garden must expand via that cell, so this solver rule marks it as a non-wall cell.
        """
        board_details = [
            'O,O,W,_',
            'W,_,_,_',
            '_,_,6,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'O,O,W,_',
            'W,O,_,_',
            '_,_,6,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_no_escape_route_adjacent_cells_blocked(self) -> None:
        """
        If a garden without a clue cannot expand due to all adjacent cells being walls, then the board is not in a
        solvable state, so an error is thrown.
        """
        board_details = [
            'O,O,W,_',
            'W,W,_,_',
            '_,5,_,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EnsureGardenWithoutClueCanExpand(board).apply_rule()

    def test_no_escape_route_adjacent_cells_not_blocked(self) -> None:
        """
        If a garden without a clue cannot expand reach a clue cell even though some adjacent cells are empty, then the
        board is not in a solvable state, so an error is thrown.
        """
        board_details = [
            'O,O,W,_',
            '_,W,_,_',
            'W,5,_,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EnsureGardenWithoutClueCanExpand(board).apply_rule()

    def test_no_clue_cell_for_garden_without_clue_to_reach(self) -> None:
        """
        A garden without a clue must expand in such a way that it reaches a clue cell. If there is no clue cell, then
        there should not be a garden so the board is not in a solvable state and an error is thrown.
        """
        board_details = [
            'O,O,W,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EnsureGardenWithoutClueCanExpand(board).apply_rule()

    def test_clue_cell_for_garden_without_clue_to_reach_is_too_far(self) -> None:
        """
        A garden without a clue must expand in such a way that it reaches a clue cell. There is a clue cell to target,
        but it is too far to reach. Therefore, the board is not in a solvable state and an error is thrown.
        """
        board_details = [
            'O,O,W,_',
            '_,_,_,_',
            '_,_,4,_',
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            EnsureGardenWithoutClueCanExpand(board).apply_rule()

    def test_non_naive_escape_route(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through to reach a clue cell. However, it must expand
        through a specific cell in order for it to be able to reach a clue cell. Therefore, that cell is marked as a
        non-wall.
        """
        board_details = [
            '_,_,_,_',
            '_,4,W,W',
            '_,_,O,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,_',
            '_,4,W,W',
            '_,O,O,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_adjacent_escape_route(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through. There is a non-adjacent cell that must be part
        of the garden or else it will prevent the garden from expanding in a way that will allow it to reach a clue
        cell. Therefore, that cell is marked as a non-wall.
        """
        board_details = [
            'W,O,O,W',
            'W,_,_,W',
            'W,_,_,W',
            '_,7,W,_',
            '_,O,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'W,O,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,7,W,_',
            '_,O,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_adjacent_escape_route_through_other_garden_cells(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through. There is a non-adjacent cell that must be part
        of the garden or else it will prevent the garden from expanding in a way that will allow it to reach a clue
        cell. This example is further complicated since the path to the escape route cell goes through another
        incomplete garden with no clue. We still expect that the escape route cell is marked as a non-wall.
        """
        board_details = [
            'W,O,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,_,W,_',
            '_,_,_,_',
            '_,8,_,_',
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithoutClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'W,O,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,O,W,_',
            '_,_,_,_',
            '_,8,_,_',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_multiple_gardens_where_solver_rule_applies(self) -> None:
        """
        If there are multiple cells where this rule applies and should be marked as non-wall cells, it requires multiple
        iterations of this solver rule to mark all the cells as non-walls. Each iteration can only mark one cell as a
        non-wall. The reason for this is that once a cell is marked as a non-wall, the set of gardens can change.
        Therefore, the set of gardens be re-derived before potentially marking another cell as a non-wall.
        """
        board_details = [
            '_,_,_,_',
            '5,_,W,W',
            '_,_,_,O',
        ]
        board = self.create_board(board_details)
        ensure_garden_without_clue_can_expand_solver_rule = EnsureGardenWithoutClueCanExpand(board)

        # First iteration of the solver rule should only change one cell
        cell_changes = ensure_garden_without_clue_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state1 = [
            '_,_,_,_',
            '5,_,W,W',
            '_,_,O,O',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state1)

        # Second iteration of the solver rule should also change one cell
        cell_changes = ensure_garden_without_clue_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state2 = [
            '_,_,_,_',
            '5,_,W,W',
            '_,O,O,O',
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)

        # On the third iteration, there are no more cells to apply this solver rule to, so the board is unchanged
        cell_changes = ensure_garden_without_clue_can_expand_solver_rule.apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)
