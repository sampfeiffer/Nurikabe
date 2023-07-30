from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board
from nurikabe.solver.path_finding import find_shortest_path_between_cells, NoPathFoundError


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

    def test_same_cell(self) -> None:
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)
        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=cell, end_cell=cell)
        self.assertEqual(shortest_path_between_cells, [cell])

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
        self.assertEqual(shortest_path_between_cells, expected)

        # The path from end_cell to start_cell should be the reverse of the path above
        backwards_path = find_shortest_path_between_cells(start_cell=end_cell, end_cell=start_cell)
        self.assertEqual(backwards_path, shortest_path_between_cells[::-1])

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
        self.assertEqual(len(shortest_path_between_cells), 4)

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
        self.assertEqual(shortest_path_between_cells, expected)

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
        self.assertEqual(shortest_path_between_cells, expected)

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
        self.assertEqual(shortest_path_between_cells, expected)
        self.assertEqual(len(shortest_path_between_cells), 16)

        # If we limit the number of length of the path to 16, this should still be considered viable
        shortest_path_between_cells_with_limit = find_shortest_path_between_cells(
            start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells, max_path_length=16
        )
        self.assertEqual(shortest_path_between_cells_with_limit, expected)

        # If we limit the number of length of the path to 15, then there is no path possible, so an error should be
        # thrown
        with self.assertRaises(NoPathFoundError):
            find_shortest_path_between_cells(start_cell=start_cell, end_cell=end_cell, off_limits_cells=off_limit_cells,
                                             max_path_length=15)
