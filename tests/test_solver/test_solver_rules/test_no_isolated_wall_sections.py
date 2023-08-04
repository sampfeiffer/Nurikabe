from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.no_isolated_wall_sections import NoIsolatedWallSections
from tests.build_board import build_board


class TestNoIsolatedWallSections(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_cell_changes(self) -> None:
        """
        If there are no cells that provide the only escape route for a wall section, then this solver rule should not
        trigger any cell changes.
        """
        board_details = [
            '1,_,_,X',
            '_,_,_,_',
            '_,3,X,_'
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_only_escape_route_for_only_wall_section(self) -> None:
        """
        If there are is a cell that provides the only escape route for a wall section, but there are no other wall
        sections to connect to, then this solver rule should not trigger any cell changes.
        """
        board_details = [
            '1,_,_,_',
            '_,_,O,_',
            '_,_,X,3'
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_only_escape_route_with_multiple_wall_sections(self) -> None:
        """
        If there are is a cell that provides the only escape route for a wall section, and there are other wall
        sections to connect to, then the escape route cell should be marked as a wall.
        """
        board_details = [
            '1,_,_,_',
            'X,_,O,_',
            '_,_,X,3'
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '1,_,_,_',
            'X,_,O,_',
            '_,X,X,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_non_naive_escape_route(self) -> None:
        """
        If a wall section must extend through a specific cell to connect to the other wall sections, ideally that escape
        route cell would be marked as a wall. However, if the wall section can still expand in other directions and is
        not immediately surrounded by adjacent cells that are all garden cells, this solver rule does not understand
        that the wall section must extend through the escape route cell.

        For example, in the test below, the wall section containing the wall in the bottom row must extend to the left
        in order to connect with the wall cell on the top left. However, since the cell immediately to the right of the
        wall cell on the bottom row is not a garden cell, this solver rule does not understand that the escape route
        cell must be a wall.
        """
        board_details = [
            'X,_,_,_',
            '_,_,O,O',
            '_,_,X,_'
        ]
        board = self.create_board(board_details)
        cell_changes = NoIsolatedWallSections(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_multiple_cells_in_only_escape_route(self) -> None:
        """
        If the wall section must extend through multiple cells that make up the escape route, It requires multiple
        iterations of this solver rule to mark all the escape route cells as walls. Each iteration can only mark one
        cell as a wall. The reason for this is that once a cell is marked as a wall, the set of wall sections can
        change. Therefore, the set of wall sections must be re-derived before potentially marking another cell as a
        wall.
        """
        board_details = [
            '_,X,_,_',
            '_,_,O,O',
            '_,_,_,X'
        ]
        board = self.create_board(board_details)
        no_isolated_wall_sections_solver_rule = NoIsolatedWallSections(board)

        # First iteration of the solver rule should only change one cell
        cell_changes = no_isolated_wall_sections_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state1 = [
            '_,X,_,_',
            '_,_,O,O',
            '_,_,X,X'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state1)

        # Second iteration of the solver rule should also change one cell
        cell_changes = no_isolated_wall_sections_solver_rule.apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state2 = [
            '_,X,_,_',
            '_,_,O,O',
            '_,X,X,X'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)

        # On the third iteration, there are no more cells to apply this solver rule to, so the board is unchanged
        cell_changes = no_isolated_wall_sections_solver_rule.apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), expected_board_state2)
