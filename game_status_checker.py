import logging

from board import Board
from game_status import GameStatus
from cell_change_info import CellChanges
from weak_garden import WeakGarden

logger = logging.getLogger(__name__)


class GameStatusChecker:
    def __init__(self, board: Board):
        self.board = board
        self.expected_number_of_garden_cells = self.get_expected_number_of_garden_cells()

    def get_expected_number_of_garden_cells(self) -> int:
        return sum(cell.clue for cell in self.board.flat_cell_list if cell.has_clue)

    def is_solution_correct(self, cell_changes: CellChanges) -> GameStatus:
        if not cell_changes.has_any_changes():
            logger.debug('no changes')
            game_status = GameStatus.IN_PROGRESS
        elif not cell_changes.has_any_wall_changes():
            logger.debug('no wall changes')
            game_status = GameStatus.IN_PROGRESS
        elif not self.has_expected_number_of_weak_garden_cells():
            logger.debug('not correct number of weak garden cells')
            game_status = GameStatus.IN_PROGRESS
        elif self.has_two_by_two_wall():
            logger.debug('has two by two wall')
            game_status = GameStatus.IN_PROGRESS
        elif not self.are_all_walls_connected():
            logger.debug('walls are not all connected')
            game_status = GameStatus.IN_PROGRESS
        else:
            weak_gardens = self.board.get_all_weak_gardens()
            if not self.do_all_weak_gardens_have_exactly_one_clue(weak_gardens):
                logger.debug('weak gardens must have exactly one clue')
                game_status = GameStatus.IN_PROGRESS
            elif not self.are_all_weak_gardens_correct_size(weak_gardens):
                logger.debug('weak garden size must equal the clue value')
                game_status = GameStatus.IN_PROGRESS
            else:
                logger.debug('correct solution!')
                game_status = GameStatus.PUZZLE_SOLVED

        return game_status

    def has_expected_number_of_weak_garden_cells(self) -> bool:
        return self.get_number_of_weak_garden_cells() == self.expected_number_of_garden_cells

    def get_number_of_weak_garden_cells(self) -> int:
        return len([cell for cell in self.board.flat_cell_list if cell.cell_state.is_weak_garden()])

    def has_two_by_two_wall(self) -> bool:
        for cell in self.board.flat_cell_list:
            if cell.does_form_two_by_two_walls():
                return True
        return False

    def are_all_walls_connected(self) -> bool:
        all_walls = [cell for cell in self.board.flat_cell_list if cell.cell_state.is_wall()]
        if len(all_walls) == 0:
            return True
        first_wall_section = self.board.get_wall_section(starting_cell=all_walls[0])
        return first_wall_section.cells == set(all_walls)

    @staticmethod
    def do_all_weak_gardens_have_exactly_one_clue(weak_gardens: set[WeakGarden]) -> bool:
        return all(weak_garden.does_have_exactly_one_clue() for weak_garden in weak_gardens)

    @staticmethod
    def are_all_weak_gardens_correct_size(weak_gardens: set[WeakGarden]) -> bool:
        return all(weak_garden.is_garden_correct_size() for weak_garden in weak_gardens)
