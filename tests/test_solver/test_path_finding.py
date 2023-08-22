from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.cell_group import CellGroup
from nurikabe.cell import Cell
from nurikabe.solver.path_finding import find_shortest_path_between_cells, find_shortest_path_between_cell_groups, \
    PathSetupError, NoPathFoundError
from tests.build_board import build_board


class TestPathFinding(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)


class TestPathFindingSetup(TestPathFinding):
    def test_start_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect PathSetupError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(PathSetupError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells={start_cell})

    def test_end_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect PathSetupError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(PathSetupError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells={end_cell})

    def test_other_cell_groups_contains_off_limits_cell(self) -> None:
        """
        The other cells groups contains a cell that is also marked as off limits, so we expect PathSetupError to be
        thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=1)
        })}
        off_limit_cells = {
            board.get_cell_from_grid(row_number=2, col_number=0),
        }

        with self.assertRaises(PathSetupError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells,
                                             other_cell_groups=other_cell_groups)

    def test_other_cell_groups_adjacent_to_start_cell_group(self) -> None:
        """
        The other cells groups contains a cell that is adjacent to the start cell group, so we expect PathSetupError to
        be thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=0)
        })}

        with self.assertRaises(PathSetupError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell,
                                             other_cell_groups=other_cell_groups)

    def test_other_cell_groups_adjacent_to_end_cell_group(self) -> None:
        """
        The other cells groups contains a cell that is adjacent to the end cell group. This is allowed, so no error
        should be thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=3)
        })}

        try:
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell,
                                             other_cell_groups=other_cell_groups)
        except PathSetupError:
            self.fail(f'find_shortest_path_between_cells raised PathSetupError unexpectedly')


class TestPathFindingBetweenCells(TestPathFinding):
    def test_same_cell(self) -> None:
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)
        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=cell, end_cell=cell)
        self.assertEqual(shortest_path_between_cells.cell_list, [cell])

    def test_path_too_long(self) -> None:
        """Set the max path length to zero. We expect NoPathFoundError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=cell, end_cell=cell, max_path_length=0)

    def test_straight_path_between_cells(self) -> None:
        """Test that the algorithm finds a straight path between cells when possible."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=1, col_number=3)

        # Trying to go from S to E
        # '_,_,_,_'
        # 'S,_,_,E'
        # '_,_,_,_'

        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell)
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
            end_cell
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)

        # The path from end_cell to start_cell should be the reverse of the path above
        backwards_path = find_shortest_path_between_cells(start_cell=end_cell, end_cell=start_cell)
        self.assertEqual(backwards_path.cell_list, shortest_path_between_cells.cell_list[::-1])

    def test_diagonal_path_between_cells(self) -> None:
        """
        Test that the algorithm finds a diagonal path between cells. Note that there are several possible paths that all
        have the same length as the shortest path - there is no one unique shortest path in this case. For this reason,
        we just test that the length of the shortest path is correct.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=1)

        # Trying to go from S to E
        # '_,E,_,_'
        # '_,_,_,_'
        # '_,_,S,_'

        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell)
        self.assertEqual(shortest_path_between_cells.path_length, 4)

    def test_path_between_cells_with_off_limit_cells(self) -> None:
        """Test that the algorithm finds a path between cells when it has to go around some off limit cells."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=1)
        off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=3)
        }

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,E,_,_'
        # '_,X,X,X'
        # '_,_,S,_'

        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell,
                                                                       off_limits_cells=off_limit_cells)
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0),
            end_cell
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)

    def test_path_between_cells_with_unimportant_off_limit_cells(self) -> None:
        """
        Test that the algorithm finds a path between cells when there are off limit cells, but the off limit cells do
        not get in the way
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=1)
        off_limit_cells = {
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=3)
        }

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,E,_,X'
        # '_,_,X,X'
        # '_,_,S,_'

        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell,
                                                                       off_limits_cells=off_limit_cells)
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=1),
            end_cell
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)

    def test_path_between_cells_with_no_possible_path(self) -> None:
        """
        Test that an error is thrown when trying to find a path between two cells if there is no possible path around
        the off limit cells.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=1)
        off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=3)
        }

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,E,_,_'
        # 'X,X,X,X'
        # '_,_,S,_'

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells)

    def test_path_between_cells_with_off_limit_cells_blocking_direct_path(self) -> None:
        """
        Test that the algorithm finds a path between cells when it has to go around some off limit cells. Here, the
        off limit cells block the more direct route, so the algorithm has to go around
        """
        board_details = [
            '_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=1)
        end_cell = board.get_cell_from_grid(row_number=4, col_number=4)
        off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=4),
            board.get_cell_from_grid(row_number=1, col_number=5),
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=4),
            board.get_cell_from_grid(row_number=3, col_number=1),
            board.get_cell_from_grid(row_number=3, col_number=2),
            board.get_cell_from_grid(row_number=3, col_number=3),
            board.get_cell_from_grid(row_number=3, col_number=4),
            board.get_cell_from_grid(row_number=3, col_number=5),
            board.get_cell_from_grid(row_number=4, col_number=3)
        }

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,_,_,_,_,_,_'
        # '_,X,X,_,X,X,_'
        # '_,S,X,_,X,_,_'
        # '_,X,X,X,X,X,_'
        # '_,_,_,X,E,_,_'

        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell,
                                                                       off_limits_cells=off_limit_cells)
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=0, col_number=6),
            board.get_cell_from_grid(row_number=1, col_number=6),
            board.get_cell_from_grid(row_number=2, col_number=6),
            board.get_cell_from_grid(row_number=3, col_number=6),
            board.get_cell_from_grid(row_number=4, col_number=6),
            board.get_cell_from_grid(row_number=4, col_number=5),
            end_cell
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 16)

        # If we limit the number of length of the path to 16, this should still be considered viable
        shortest_path_between_cells_with_limit = find_shortest_path_between_cells(
            start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells, max_path_length=16
        )
        self.assertEqual(shortest_path_between_cells_with_limit.cell_list, expected)

        # If we limit the number of length of the path to 15, then there is no path possible, so an error should be
        # thrown
        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells,
                                             max_path_length=15)

    def test_path_between_cells_adjacent_with_other_too_large_cell_group(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group. The path length increases to
        include the number of cells in the adjacent cell group. If the max path length is too small to allow the
        additional cells from the adjacent cell group, then we expect an error to be thrown.
        """
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2)
        })}

        # Trying to go from S to E, with other cell groups marked as 'O'
        # 'E,_,_',
        # '_,O,O',
        # 'S,_,_'

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, max_path_length=4,
                                             other_cell_groups=other_cell_groups)

    def test_path_between_cells_adjacent_with_other_small_enough_cell_group(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group. The path length increases to
        include the number of cells in the adjacent cell group. If the max path length is large enough, then this
        inclusion is allowed.
        """
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2)
        })}

        # Trying to go from S to E, with other cell groups marked as 'O'
        # 'E,_,_',
        # '_,O,O',
        # 'S,_,_'

        shortest_path_between_cells = find_shortest_path_between_cells(
            start_cell=start_cell,
            end_cell=end_cell,
            max_path_length=5,
            other_cell_groups=other_cell_groups
        )
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=1, col_number=0),
            end_cell
        ]

        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 5)

    def test_path_between_cells_adjacent_with_other_small_enough_cell_group_in_multiple_places(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group multiple times. The path length
        increases to include the number of cells in the adjacent cell group, but only one time. If the max path length
        is large enough, then this inclusion is allowed.
        """
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,_,_',
            '_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=3, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2)
        })}

        # Trying to go from S to E, with other cell groups marked as 'O'
        # 'E,_,_',
        # '_,O,_',
        # '_,O,O',
        # 'S,_,_'

        shortest_path_between_cells = find_shortest_path_between_cells(
            start_cell=start_cell,
            end_cell=end_cell,
            max_path_length=7,
            other_cell_groups=other_cell_groups
        )
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            end_cell
        ]

        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 7)

    def test_path_between_cells_leverage_other_cell_group(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group. The path can than either go
        through the other cell group or go around. The number of physical cells the path must pass through is larger for
        the path through the other cell group. The path should go through the other cell group since once the path
        passes adjacent to it (which it must), there is zero cost to passing through the rest of the cell group.
        Whereas going the other way, will not allow the path to take advantage of this. The total "cost" of the path is
        smaller if the path leverages the other cell group.
        """
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,_,_',
            '_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=3, col_number=1)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        other_cell_groups = {CellGroup(cells={
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=2)
        })}

        off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=3, col_number=0),
            board.get_cell_from_grid(row_number=3, col_number=2)
        }

        # Trying to go from S to E, with other cell groups marked as 'O' and off limits cells marked as 'X'
        # 'E,_,O',
        # '_,X,O',
        # '_,_,O',
        # 'X,S,X'

        shortest_path_between_cells = find_shortest_path_between_cells(
            start_cell=start_cell,
            end_cell=end_cell,
            off_limits_cells=off_limit_cells,
            other_cell_groups=other_cell_groups
        )
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=1),
            end_cell
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 7)

    def test_path_between_cells_adjacent_with_multiple_cell_groups(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to multiple other cell groups. The path length increases
        to include the number of cells in each adjacent cell group. If the max path length is large enough, then this
        inclusion is allowed.
        """
        board_details = [
            '_,_,_,_,_',
            '_,_,_,_,_',
            '_,_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=2, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=2)
        other_cell_groups = {
            CellGroup(cells={
                board.get_cell_from_grid(row_number=1, col_number=0),
                board.get_cell_from_grid(row_number=1, col_number=1)
            }),
            CellGroup(cells={
                board.get_cell_from_grid(row_number=1, col_number=3),
                board.get_cell_from_grid(row_number=1, col_number=4)
            })
        }
        off_limit_cells = {
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=3)
        }

        # Trying to go from S to E, with other cell groups marked as 'O' and off limit cells marked as 'X'
        # '_,_,E,_,_',
        # 'O,O,_,O,O',
        # '_,X,S,X,_'

        shortest_path_between_cells = find_shortest_path_between_cells(
            start_cell=start_cell,
            end_cell=end_cell,
            off_limits_cells=off_limit_cells,
            max_path_length=7,
            other_cell_groups=other_cell_groups
        )
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=1, col_number=2),
            end_cell
        ]

        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 7)

    def test_go_long_way_around_due_to_large_other_cell_group(self) -> None:
        """
        The path from start cell to end cell has two choices.
        1. Go through few physical cells but pass adjacent to a large other cell group.
        2. Go through many physical cells, but don't pass adjacent to a large other cell group.

        In this case, option 2 is cheaper since the cell group adds "length" to the short physical path that makes is
        "longer" than the physically longer path.
        """
        board_details = [
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_',
            '_,_,_,_,_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=7, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=7, col_number=7)

        cells_in_other_cell_group: set[Cell] = set()
        for row_num in (2, 3, 4, 5):
            for col_num in (2, 3, 4, 5):
                cells_in_other_cell_group.add(board.get_cell_from_grid(row_number=row_num, col_number=col_num))
        cells_in_other_cell_group.add(board.get_cell_from_grid(row_number=6, col_number=4))
        other_cell_groups = {CellGroup(cells=cells_in_other_cell_group)}

        off_limit_cells: set[Cell] = set()
        for row_num in (1, 6):
            for col_num in range(1, 7):
                if not (row_num == 6 and col_num == 4):
                    off_limit_cells.add(board.get_cell_from_grid(row_number=row_num, col_number=col_num))
        for col_num in (1, 6):
            for row_num in range(1, 7):
                off_limit_cells.add(board.get_cell_from_grid(row_number=row_num, col_number=col_num))

        # Trying to go from S to E, with other cell groups marked as 'O' and off limit cells marked as 'X'
        # '_,_,_,_,_,_,_,_',
        # '_,X,X,X,X,X,X,_',
        # '_,X,O,O,O,O,X,_',
        # '_,X,O,O,O,O,X,_',
        # '_,X,O,O,O,O,X,_',
        # '_,X,O,O,O,O,X,_',
        # '_,X,X,X,O,X,X,_',
        # 'S,_,_,_,_,_,_,E'

        shortest_path_between_cells = find_shortest_path_between_cells(
            start_cell=start_cell,
            end_cell=end_cell,
            off_limits_cells=off_limit_cells,
            other_cell_groups=other_cell_groups
        )
        expected = [
            start_cell,
            board.get_cell_from_grid(row_number=6, col_number=0),
            board.get_cell_from_grid(row_number=5, col_number=0),
            board.get_cell_from_grid(row_number=4, col_number=0),
            board.get_cell_from_grid(row_number=3, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=0, col_number=4),
            board.get_cell_from_grid(row_number=0, col_number=5),
            board.get_cell_from_grid(row_number=0, col_number=6),
            board.get_cell_from_grid(row_number=0, col_number=7),
            board.get_cell_from_grid(row_number=1, col_number=7),
            board.get_cell_from_grid(row_number=2, col_number=7),
            board.get_cell_from_grid(row_number=3, col_number=7),
            board.get_cell_from_grid(row_number=4, col_number=7),
            board.get_cell_from_grid(row_number=5, col_number=7),
            board.get_cell_from_grid(row_number=6, col_number=7),
            end_cell
        ]

        self.assertEqual(shortest_path_between_cells.cell_list, expected)
        self.assertEqual(shortest_path_between_cells.path_length, 22)


class TestPathFindingBetweenCellGroups(TestPathFinding):
    def test_overlapping_cell_groups(self) -> None:
        """
        Note that based on the design of the path finding algorithm, the exact cells included in this path are not
        guaranteed. Only the length of the path is guaranteed to be consistent
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=3)
        })

        end_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=3)
        })

        shortest_path_between_cell_groups = find_shortest_path_between_cell_groups(start_cell_group, end_cell_group)
        self.assertEqual(shortest_path_between_cell_groups.path_length, 1)

    def test_path_between_cell_groups(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,_,_,_,_,_',
            '_,_,_,_,_,_',
            '_,_,_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=4)
        })

        end_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=3, col_number=1)
        })

        # Trying to go from S to E
        # '_,_,_,S,_,_'
        # '_,_,_,S,S,_'
        # '_,E,_,_,_,_'
        # '_,E,_,_,_,_'

        shortest_path_between_cell_groups = find_shortest_path_between_cell_groups(start_cell_group, end_cell_group)
        self.assertEqual(shortest_path_between_cell_groups.path_length, 4)

    def test_path_between_cell_groups_with_off_limits(self) -> None:
        board_details = [
            '_,_,_,_,_,_',
            '_,_,_,_,_,_',
            '_,_,_,_,_,_',
            '_,_,_,_,_,_'
        ]
        board = self.create_board(board_details)
        start_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=0, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=3),
            board.get_cell_from_grid(row_number=1, col_number=4)
        })

        end_cell_group = CellGroup(cells={
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=3, col_number=1)
        })

        off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=3)
        }

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,_,_,S,_,_'
        # '_,_,X,S,S,_'
        # '_,E,X,X,_,_'
        # '_,E,_,_,_,_'

        shortest_path_between_cell_groups = find_shortest_path_between_cell_groups(start_cell_group, end_cell_group,
                                                                                   off_limit_cells)
        self.assertEqual(shortest_path_between_cell_groups.path_length, 5)

        # The path length is 5, so if we set the limit to 5, it still should not throw and error
        shortest_path_between_cell_groups = find_shortest_path_between_cell_groups(start_cell_group, end_cell_group,
                                                                                   off_limit_cells, max_path_length=5)
        self.assertEqual(shortest_path_between_cell_groups.path_length, 5)

        # If we set the max length to 4, then there is no possible path
        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cell_groups(start_cell_group, end_cell_group, off_limit_cells, max_path_length=4)

        # Block another cell so that the shortest path goes around the other way
        off_limit_cells.add(board.get_cell_from_grid(row_number=1, col_number=1))

        # Trying to go from S to E, with off limits cells marked as 'X'
        # '_,_,_,S,_,_'
        # '_,X,X,S,S,_'
        # '_,E,X,X,_,_'
        # '_,E,_,_,_,_'
        shortest_path_between_cell_groups = find_shortest_path_between_cell_groups(start_cell_group, end_cell_group,
                                                                                   off_limit_cells)
        self.assertEqual(shortest_path_between_cell_groups.path_length, 6)

        # Block off two more cells so that there is no possible path
        off_limit_cells.add(board.get_cell_from_grid(row_number=0, col_number=0))
        off_limit_cells.add(board.get_cell_from_grid(row_number=3, col_number=3))

        # Trying to go from S to E, with off limits cells marked as 'X'
        # 'X,_,_,S,_,_'
        # '_,X,X,S,S,_'
        # '_,E,X,X,_,_'
        # '_,E,_,X,_,_'
        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cell_groups(start_cell_group, end_cell_group, off_limit_cells)
