from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.cell_group import CellGroup
from nurikabe.solver.path_finding import PathFinder, NoPathFoundError
from ...build_board import build_board
from .build_path_finder import build_path_finder, extract_blank_board_details, PathFinderInfo


class TestPathFinding(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, extract_blank_board_details(board_details))

    def create_path_finder(self, board_details: list[str]) -> PathFinderInfo:
        return build_path_finder(self.screen, board_details)


class TestPathFindingBetweenCells(TestPathFinding):
    def test_same_cell(self) -> None:
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_'
        ]
        board = self.create_board(board_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)
        shortest_path_between_cells = PathFinder(start_cell_group=cell, end_cell_group=cell).get_path_info()
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
            PathFinder(start_cell_group=cell, end_cell_group=cell).get_path_info(max_path_length=0)

    def test_straight_path_between_cells(self) -> None:
        """Test that the algorithm finds a straight path between cells when possible."""
        board_details = [
            '_,_,_,_',
            'S,_,_,E',
            '_,_,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        shortest_path_between_cells = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=3)
        ]
        self.assertEqual(shortest_path_between_cells.cell_list, expected)

        # The path from end_cell to start_cell should be the reverse of the path above
        backwards_path = PathFinder(start_cell_group=path_finder.end_cell_group,
                                    end_cell_group=path_finder.start_cell_group).get_path_info()
        self.assertEqual(backwards_path.cell_list, shortest_path_between_cells.cell_list[::-1])

    def test_diagonal_path_between_cells(self) -> None:
        """
        Test that the algorithm finds a diagonal path between cells. Note that there are several possible paths that all
        have the same length as the shortest path - there is no one unique shortest path in this case. For this reason,
        we just test that the length of the shortest path is correct.
        """
        board_details = [
            '_,E,_,_',
            '_,_,_,_',
            '_,_,S,_'
        ]
        path_finder = self.create_path_finder(board_details).path_finder

        shortest_path_between_cells = path_finder.get_path_info()
        self.assertEqual(shortest_path_between_cells.path_length, 4)

    def test_path_between_cells_with_off_limit_cells(self) -> None:
        """Test that the algorithm finds a path between cells when it has to go around some off limit cells."""
        board_details = [
            '_,E,_,_',
            '_,X,X,X',
            '_,_,S,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=1)
        ]
        self.assertEqual(path_info.cell_list, expected)

    def test_path_between_cells_with_unimportant_off_limit_cells(self) -> None:
        """
        Test that the algorithm finds a path between cells when there are off limit cells, but the off limit cells do
        not get in the way
        """
        board_details = [
            '_,E,_,X',
            '_,_,X,X',
            '_,_,S,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=1)
        ]
        self.assertEqual(path_info.cell_list, expected)

    def test_path_between_cells_with_no_possible_path(self) -> None:
        """
        Test that an error is thrown when trying to find a path between two cells if there is no possible path around
        the off limit cells.
        """
        board_details = [
            '_,E,_,_',
            'X,X,X,X',
            '_,_,S,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        with self.assertRaises(NoPathFoundError):
            path_finder_info.path_finder.get_path_info()

    def test_path_between_cells_with_off_limit_cells_blocking_direct_path(self) -> None:
        """
        Test that the algorithm finds a path between cells when it has to go around some off limit cells. Here, the
        off limit cells block the more direct route, so the algorithm has to go around
        """
        board_details = [
            '_,_,_,_,_,_,_',
            '_,X,X,_,X,X,_',
            '_,S,X,_,X,_,_',
            '_,X,X,X,X,X,_',
            '_,_,_,X,E,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=2, col_number=1),
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
            board.get_cell_from_grid(row_number=4, col_number=4)
        ]
        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 16)

        # If we limit the number of length of the path to 16, this should still be considered viable
        path_info_with_limit = path_finder.get_path_info(max_path_length=16)
        self.assertEqual(path_info_with_limit.cell_list, expected)

        # If we limit the number of length of the path to 15, then there is no path possible, so an error should be
        # thrown
        with self.assertRaises(NoPathFoundError):
            path_finder.get_path_info(max_path_length=15)

    def test_path_between_cells_adjacent_with_other_too_large_cell_group(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group. The path length increases to
        include the number of cells in the adjacent cell group. If the max path length is too small to allow the
        additional cells from the adjacent cell group, then we expect an error to be thrown.
        """
        board_details = [
            'E,_,_',
            '_,a,a',
            'S,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        with self.assertRaises(NoPathFoundError):
            path_finder_info.path_finder.get_path_info(max_path_length=4)

    def test_path_between_cells_adjacent_with_other_small_enough_cell_group(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group. The path length increases to
        include the number of cells in the adjacent cell group. If the max path length is large enough, then this
        inclusion is allowed.
        """
        board_details = [
            'E,_,_',
            '_,a,a',
            'S,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info(max_path_length=5)
        expected = [
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0)
        ]

        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 5)

    def test_path_between_cells_adjacent_with_other_small_enough_cell_group_in_multiple_places(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to another cell group multiple times. The path length
        increases to include the number of cells in the adjacent cell group, but only one time. If the max path length
        is large enough, then this inclusion is allowed.
        """
        board_details = [
            'E,_,_',
            '_,a,_',
            '_,a,a',
            'S,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info(max_path_length=7)
        expected = [
            board.get_cell_from_grid(row_number=3, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=0),
            board.get_cell_from_grid(row_number=1, col_number=0),
            board.get_cell_from_grid(row_number=0, col_number=0)
        ]

        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 7)

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
            'E,_,a',
            '_,X,a',
            '_,_,a',
            'X,S,X'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=3, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=1),
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=0)
        ]
        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 7)

    def test_path_between_cells_adjacent_with_multiple_cell_groups(self) -> None:
        """
        The path from start cell to end cell must pass adjacent to multiple other cell groups. The path length increases
        to include the number of cells in each adjacent cell group. If the max path length is large enough, then this
        inclusion is allowed.
        """
        board_details = [
            '_,_,E,_,_',
            'a,a,_,b,b',
            '_,X,S,X,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info(max_path_length=7)
        expected = [
            board.get_cell_from_grid(row_number=2, col_number=2),
            board.get_cell_from_grid(row_number=1, col_number=2),
            board.get_cell_from_grid(row_number=0, col_number=2)
        ]

        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 7)

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
            '_,X,X,X,X,X,X,_',
            '_,X,a,a,a,a,X,_',
            '_,X,a,a,a,a,X,_',
            '_,X,a,a,a,a,X,_',
            '_,X,a,a,a,a,X,_',
            '_,X,X,X,a,X,X,_',
            'S,_,_,_,_,_,_,E'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        path_info = path_finder.get_path_info()
        expected = [
            board.get_cell_from_grid(row_number=7, col_number=0),
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
            board.get_cell_from_grid(row_number=7, col_number=7)
        ]

        self.assertEqual(path_info.cell_list, expected)
        self.assertEqual(path_info.path_length, 22)


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

        shortest_path_between_cell_groups = PathFinder(start_cell_group=start_cell_group,
                                                       end_cell_group=end_cell_group).get_path_info()
        self.assertEqual(shortest_path_between_cell_groups.path_length, 1)

    def test_path_between_cell_groups(self) -> None:
        board_details = [
            '_,_,_,S,_,_',
            '_,_,_,S,S,_',
            '_,E,_,_,_,_',
            '_,E,_,_,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_info = path_finder_info.path_finder.get_path_info()
        self.assertEqual(path_info.path_length, 4)

    def test_path_between_cell_groups_with_off_limit_cells(self) -> None:
        board_details = [
            '_,_,_,S,_,_',
            '_,_,X,S,S,_',
            '_,E,X,X,_,_',
            '_,E,_,_,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        path_finder = path_finder_info.path_finder

        path_info = path_finder.get_path_info()
        self.assertEqual(path_info.path_length, 5)

        # The path length is 5, so if we set the limit to 5, it still should not throw an error
        path_info = path_finder.get_path_info(max_path_length=5)
        self.assertEqual(path_info.path_length, 5)

        # If we set the max length to 4, then there is no possible path
        with self.assertRaises(NoPathFoundError):
            path_finder.get_path_info(max_path_length=4)

    def test_path_between_cell_groups_with_no_possible_path(self) -> None:
        board_details = [
            'X,_,_,S,_,_',
            '_,X,X,S,S,_',
            '_,E,X,X,_,_',
            '_,E,_,X,_,_'
        ]
        path_finder_info = self.create_path_finder(board_details)
        with self.assertRaises(NoPathFoundError):
            path_finder_info.path_finder.get_path_info()
