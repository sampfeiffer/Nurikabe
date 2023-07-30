from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board
from nurikabe.solver.path_finding import find_shortest_path_between_cells, find_shortest_path_between_cell_groups, \
    NoPathFoundError
from nurikabe.cell_group import CellGroup


class TestPathFinding(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    @staticmethod
    def create_level_from_string_list(level_details: list[str]) -> Level:
        return LevelBuilderFromStringList(level_details).build_level()

    def create_board(self, level_details: list[str]) -> Board:
        level = self.create_level_from_string_list(level_details)
        return Board(level, self.screen)


class TestPathFindingBetweenCells(TestPathFinding):
    def test_same_cell(self) -> None:
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)
        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=cell, end_cell=cell)
        self.assertEqual(shortest_path_between_cells.cell_list, [cell])

    def test_path_too_long(self) -> None:
        """Set the max path length to zero. We expect NoPathFoundError to be thrown."""
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=cell, end_cell=cell, max_path_length=0)

    def test_start_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect NoPathFoundError to be thrown."""
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells={start_cell})

    def test_end_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect NoPathFoundError to be thrown."""
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells={end_cell})

    def test_straight_path_between_cells(self) -> None:
        """Test that the algorithm finds a straight path between cells when possible."""
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,,,,',
            ',,,,,,',
            ',,,,,,',
            ',,,,,,',
            ',,,,,,'
        ]
        board = self.create_board(level_details)
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


class TestPathFindingBetweenCellGroups(TestPathFinding):
    def test_overlapping_cell_groups(self) -> None:
        """
        Note that based on the design of the path finding algorithm, the exact cells included in this path are not
        guaranteed. Only the length of the path is guaranteed to be consistent
        """
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,,,',
            ',,,,,',
            ',,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)
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
        level_details = [
            ',,,,,',
            ',,,,,',
            ',,,,,',
            ',,,,,'
        ]
        board = self.create_board(level_details)
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
