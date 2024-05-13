from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.cell_group import CellGroup

from .build_path_finder import BadPathFinderSetupError, PathFinderInfo, build_path_finder


class TestBuildPathFinder(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.screen = MagicMock(name='Screen')

    def create_path_finder_info(self, board_details: list[str]) -> PathFinderInfo:
        return build_path_finder(self.screen, board_details)

    def test_no_start_cells(self) -> None:
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,E,_',
        ]
        with self.assertRaises(BadPathFinderSetupError):
            self.create_path_finder_info(board_details)

    def test_no_end_cells(self) -> None:
        board_details = [
            '_,_,_',
            '_,_,_',
            '_,S,_',
        ]
        with self.assertRaises(BadPathFinderSetupError):
            self.create_path_finder_info(board_details)

    def test_unsupported_uppercase_character(self) -> None:
        for unsupported_character in 'AO':
            board_details = [
                '_,_,_',
                f'{unsupported_character},_,_',
                '_,_,_',
            ]
            with self.assertRaises(BadPathFinderSetupError):
                self.create_path_finder_info(board_details)

    def test_missing_characters(self) -> None:
        board_details = [
            '_,,_',
            '_,_,_',
            '_,_,_',
        ]
        with self.assertRaises(BadPathFinderSetupError):
            self.create_path_finder_info(board_details)

    def test_too_many_characters(self) -> None:
        board_details = [
            '_,__,_',
            '_,_,_',
            '_,_,_',
        ]
        with self.assertRaises(BadPathFinderSetupError):
            self.create_path_finder_info(board_details)

    def test_proper_setup(self) -> None:
        board_details = [
            'S,E,E',
            '_,X,X',
            'S,_,c',
            '_,a,a',
        ]
        path_finder_info = self.create_path_finder_info(board_details)
        path_finder = path_finder_info.path_finder
        board = path_finder_info.board

        expected_start_cells = {
            board.get_cell_from_grid(row_number=0, col_number=0),
            board.get_cell_from_grid(row_number=2, col_number=0),
        }
        self.assertEqual(path_finder.start_cell_group.cells, expected_start_cells)

        expected_end_cells = {
            board.get_cell_from_grid(row_number=0, col_number=1),
            board.get_cell_from_grid(row_number=0, col_number=2),
        }
        self.assertEqual(path_finder.end_cell_group.cells, expected_end_cells)

        expected_off_limit_cells = {
            board.get_cell_from_grid(row_number=1, col_number=1),
            board.get_cell_from_grid(row_number=1, col_number=2),
        }
        self.assertEqual(path_finder.off_limit_cells, expected_off_limit_cells)

        expected_other_cell_groups = {
            CellGroup(cells={
                board.get_cell_from_grid(row_number=3, col_number=1),
                board.get_cell_from_grid(row_number=3, col_number=2),
            }),
            CellGroup(cells={
                board.get_cell_from_grid(row_number=2, col_number=2),
            }),
        }
        self.assertEqual(path_finder.other_cell_groups, expected_other_cell_groups)
