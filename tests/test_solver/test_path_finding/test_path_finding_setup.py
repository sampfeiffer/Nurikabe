from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.board import Board
from nurikabe.cell_group import CellGroup
from nurikabe.solver.path_finding import PathFinder, PathSetupError
from tests.build_board import build_board


class TestPathFindingSetup(TestCase):
    screen = MagicMock(name='Screen')

    def create_board(self, board_details: list[str]) -> Board:
        return build_board(self.screen, board_details)

    def test_start_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect PathSetupError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(PathSetupError):
            PathFinder(start_cell_group=start_cell, end_cell_group=end_cell, off_limit_cells=frozenset({start_cell}))

    def test_end_cell_off_limits(self) -> None:
        """Since the start cell is off limits, we expect PathSetupError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=1, col_number=2)
        end_cell = board.get_cell_from_grid(row_number=2, col_number=3)

        with self.assertRaises(PathSetupError):
            PathFinder(start_cell_group=start_cell, end_cell_group=end_cell, off_limit_cells=frozenset({end_cell}))

    def test_other_cell_groups_contains_off_limit_cell(self) -> None:
        """
        The other cells groups contains a cell that is also marked as off limits, so we expect PathSetupError to be
        thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {
            CellGroup(
                cells={
                    board.get_cell_from_grid(row_number=2, col_number=0),
                    board.get_cell_from_grid(row_number=2, col_number=1),
                }
            )
        }
        off_limit_cells = {
            board.get_cell_from_grid(row_number=2, col_number=0),
        }

        with self.assertRaises(PathSetupError):
            PathFinder(
                start_cell_group=start_cell,
                end_cell_group=end_cell,
                off_limit_cells=frozenset(off_limit_cells),
                other_cell_groups=frozenset(other_cell_groups),
            )

    def test_other_cell_groups_adjacent_to_start_cell_group(self) -> None:
        """
        The other cells groups contains a cell that is adjacent to the start cell group, so we expect PathSetupError to
        be thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {
            CellGroup(
                cells={
                    board.get_cell_from_grid(row_number=1, col_number=0),
                }
            )
        }

        with self.assertRaises(PathSetupError):
            PathFinder(
                start_cell_group=start_cell, end_cell_group=end_cell, other_cell_groups=frozenset(other_cell_groups)
            )

    def test_other_cell_groups_adjacent_to_end_cell_group(self) -> None:
        """
        The other cells groups contains a cell that is adjacent to the end cell group. This is allowed, so no error
        should be thrown.
        """
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {
            CellGroup(
                cells={
                    board.get_cell_from_grid(row_number=1, col_number=3),
                }
            )
        }

        try:
            PathFinder(
                start_cell_group=start_cell, end_cell_group=end_cell, other_cell_groups=frozenset(other_cell_groups)
            )
        except PathSetupError:
            self.fail('find_shortest_path_between_cells raised PathSetupError unexpectedly')

    def test_overlapping_other_cell_groups(self) -> None:
        """There is a cell that is in more than one other cell group, so we expect PathSetupError to be thrown."""
        board_details = [
            '_,_,_,_',
            '_,_,_,_',
            '_,_,_,_',
        ]
        board = self.create_board(board_details)
        start_cell = board.get_cell_from_grid(row_number=0, col_number=0)
        end_cell = board.get_cell_from_grid(row_number=0, col_number=3)
        other_cell_groups = {
            CellGroup(
                cells={
                    board.get_cell_from_grid(row_number=1, col_number=3),
                    board.get_cell_from_grid(row_number=2, col_number=3),
                }
            ),
            CellGroup(
                cells={
                    board.get_cell_from_grid(row_number=2, col_number=2),
                    board.get_cell_from_grid(row_number=2, col_number=3),
                }
            ),
        }

        with self.assertRaises(PathSetupError):
            PathFinder(
                start_cell_group=start_cell, end_cell_group=end_cell, other_cell_groups=frozenset(other_cell_groups)
            )
