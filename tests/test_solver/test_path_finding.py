from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board
from nurikabe.solver.path_finding import find_shortest_path_between_cells


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

    def test_find_shortest_path_same_cell(self) -> None:
        level_details = [
            ',,,',
            ',,,',
            ',,,'
        ]
        board = self.create_board(level_details)
        cell = board.get_cell_from_grid(row_number=1, col_number=2)
        shortest_path_between_cells = find_shortest_path_between_cells(start_cell=cell, end_cell=cell,
                                                                       off_limits_cells=set())
        self.assertEqual(shortest_path_between_cells, [cell])
