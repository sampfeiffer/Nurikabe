from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.ensure_garden_with_clue_can_expand import EnsureGardenWithClueCanExpand, \
    NoPossibleSolutionFromCurrentState
from tests.build_board import build_board


class TestEnsureGardenWithClueCanExpand(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """
        There are no gardens with a clue that need to expand via a single cell, so the board is not impacted by this
        solver rule.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            'O,3,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_no_cell_change_for_garden_without_clue(self) -> None:
        """
        This solver rule only applies to a garden with a clue. even though there is a garden without a clue that needs
        to expand through a single cell, no changes are applied by this rule.
        """
        board_details = [
            '3,_,_,_',
            '_,_,_,_',
            'O,W,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
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
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,_',
            'O,W,_,_',
            'O,3,W,_'
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
            EnsureGardenWithClueCanExpand(board).apply_rule()

    def test_no_escape_route_for_garden_with_clue_adjacent_cells_blocked(self) -> None:
        """
        If an undersized garden cannot expand due to all adjacent cells being walls, then the board is not in a solvable
        state, so an error is thrown.
        """
        board_details = [
            '3,O,W,_',
            'W,W,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentState):
            EnsureGardenWithClueCanExpand(board).apply_rule()

    def test_no_escape_route_adjacent_cells_not_blocked(self) -> None:
        """
        If an undersized garden cannot expand the appropriate amount even though some adjacent cells are empty, then the
        board is not in a solvable state, so an error is thrown.
        """
        board_details = [
            '6,O,W,_',
            '_,_,W,_',
            '_,W,_,_'
        ]
        board = self.create_board(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentState):
            EnsureGardenWithClueCanExpand(board).apply_rule()

    def test_non_naive_escape_route(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through. However, it must expand through a specific cell
        in order to have enough room for the required garden size. Therefore, that cell is marked as a non-wall.
        """
        board_details = [
            '_,_,_,_',
            '_,_,W,W',
            '_,_,3,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,_',
            '_,_,W,W',
            '_,O,3,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_adjacent_escape_route(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through. There is a non-adjacent cell that must be part
        of the garden or else it will prevent the garden from expanding to the appropriate size. Therefore, that cell is
        marked as a non-wall.
        """
        board_details = [
            'W,6,O,W',
            'W,_,_,W',
            'W,_,_,W',
            '_,_,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'W,6,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,_,W,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_adjacent_escape_route_through_other_garden_cells(self) -> None:
        """
        A garden has multiple adjacent cells that it can expand through. There is a non-adjacent cell that must be part
        of the garden or else it will prevent the garden from expanding to the appropriate size. This example is further
        complicated since the path to the escape route cell goes through an incomplete garden with no clue. We still
        expect that the escape route cell is marked as a non-wall.
        """
        board_details = [
            'W,7,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,_,W,_'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            'W,7,O,W',
            'W,_,_,W',
            'W,O,_,W',
            '_,O,W,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_escape_route_unique_due_to_off_limit_cells_from_other_garden_with_clue(self) -> None:
        """
        A garden has a single escape route since there is another garden with a clue that is causing its adjacent cells
        to be off limits. We expect that escape route cell to be marked as a non-wall.
        """
        board_details = [
            '_,W,5,O,W',
            '_,_,_,_,W',
            '_,_,_,O,W',
            '_,_,_,O,4'
        ]
        board = self.create_board(board_details)
        cell_changes = EnsureGardenWithClueCanExpand(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,W,5,O,W',
            '_,_,O,_,W',
            '_,_,_,O,W',
            '_,_,_,O,4'
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
            '_,_,W,W',
            '_,_,_,3'
        ]
        board = self.create_board(board_details)
        ensure_garden_with_clue_can_expand_solver_rule = EnsureGardenWithClueCanExpand(board)

        # First iteration of the solver rule should only change one cell
        cell_changes = ensure_garden_with_clue_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state1 = [
            '_,_,_,_',
            '_,_,W,W',
            '_,_,O,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state1)

        # Second iteration of the solver rule should also change one cell
        cell_changes = ensure_garden_with_clue_can_expand_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state2 = [
            '_,_,_,_',
            '_,_,W,W',
            '_,O,O,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)

        # On the third iteration, there are no more cells to apply this solver rule to, so the board is unchanged
        cell_changes = ensure_garden_with_clue_can_expand_solver_rule.apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)
