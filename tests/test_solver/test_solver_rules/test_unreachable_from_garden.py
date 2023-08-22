from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.solver.solver_rules.unreachable_from_garden import UnreachableFromGarden
from tests.build_board import build_board


class TestUnreachableFromGarden(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_no_unreachable_cells(self) -> None:
        """All cells are reachable from a garden, so this solver rule should have no impact."""
        board_details = [
            '_,_,_,_',
            '_,5,X,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_unreachable_cell_due_to_indirect_path(self) -> None:
        """
        An empty cell is Manhattan reachable from a clue cell, but due to a wall, that direct route to that empty cell
        is blocked. The path must instead go around the wall. Since that indirect path is too long, the empty cell is
        marked as a wall cell.
        """
        board_details = [
            '_,_,_,_',
            '_,4,X,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,_',
            '_,4,X,X',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_unreachable_cell_due_to_cutoff_region_via_walls(self) -> None:
        """
        An empty cell is Manhattan reachable from a clue cell, but due to walls, there is no path to that empty cell.
        The empty cell is therefore marked as a wall cell.
        """
        board_details = [
            '_,_,X,_',
            '_,4,_,X',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,X,X',
            '_,4,_,X',
            '_,_,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_unreachable_cell_due_to_cutoff_region_via_neighboring_garden(self) -> None:
        """
        An empty cell is Manhattan reachable from a clue cell, but due to other gardens making cells off limits, there
        is no path to that empty cell. The empty cell is therefore marked as a wall cell.
        """
        board_details = [
            '_,_,_,X',
            '4,X,O,O',
            '_,_,X,3'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,X,X',
            '4,X,O,O',
            '_,_,X,3'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_unreachable_cell_due_to_existing_garden_size(self) -> None:
        """
        An empty cell is Manhattan reachable from a clue cell. However, the clue cell is part of a garden where there
        are other non-wall cells. The empty cell is out of reach from the garden given the remaining size of the garden.
        The empty cell is therefore marked as a wall cell.
        """
        board_details = [
            '_,_,_,_',
            '_,4,_,_',
            '_,O,_,_'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,X',
            '_,4,_,_',
            '_,O,_,_'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_unreachable_cell_due_to_adjacent_garden_without_clue(self) -> None:
        """
        An empty cell is Manhattan reachable from a garden. However, a cell adjacent to the empty cell is marked a 
        non-wall cell and is not part of a garden with a clue. By marking the empty cell as a non-wall, we would 
        effectively be making both the empty cell and the adjacent cell part of the garden and in this case, making the
        garden too large. The empty cell is therefore marked as a wall cell.
        """
        board_details = [
            '_,_,_,X',
            '_,4,_,_',
            '_,O,_,O'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,_,_,X',
            '_,4,_,X',
            '_,O,_,O'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_reachable_cell_even_with_adjacent_garden_without_clue(self) -> None:
        """
        An empty cell is Manhattan reachable from a garden. However, a cell adjacent to the empty cell is marked a
        non-wall cell and is not part of a garden with a clue. By marking the empty cell as a non-wall, we would
        effectively be making both the empty cell and the adjacent cell part of the garden. In this case, the original
        garden is large enough to incorporate both cells. Therefore, the empty cell cannot be marked as a wall cell.
        """
        board_details = [
            '_,_,_,X',
            '_,5,_,_',
            '_,O,_,O'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)

    def test_unreachable_cell_due_to_too_large_incomplete_garden_without_clue(self) -> None:
        """
        An empty cell is Manhattan reachable from a garden. However, the path to the empty cell passes adjacent to an
        incomplete garden without a clue. By passing this incomplete garden, the source garden would increase by too
        much making the garden too large. The empty cell is therefore marked as a wall cell.
        """
        board_details = [
            '_,X,X,X',
            '4,_,_,_',
            'X,O,X,X'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertTrue(cell_changes.has_any_changes())
        expected_board_state = [
            '_,X,X,X',
            '4,_,_,X',
            'X,O,X,X'
        ]
        self.assertEqual(board.as_simple_string_list(), expected_board_state)

    def test_reachable_cell_even_with_passing_incomplete_garden_without_clue(self) -> None:
        """
        An empty cell is Manhattan reachable from a garden. However, the path to the empty cell passes adjacent to an
        incomplete garden without a clue. By passing this incomplete garden, the source garden would increase by the
        size of the incomplete garden. The clue is large enough to incorporate this. Therefore, the empty cell cannot be
        marked as a wall cell.
        """
        board_details = [
            '_,X,X,X',
            '5,_,_,_',
            'X,O,X,X'
        ]
        board = self.create_board(board_details)
        cell_changes = UnreachableFromGarden(board).apply_rule()
        self.assertFalse(cell_changes.has_any_changes())
        self.assertEqual(board.as_simple_string_list(), board_details)
