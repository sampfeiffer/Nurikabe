from board import Board
from game_status import GameStatus
from cell_change_info import CellChangeInfo
from cell_state import CellState


class GameStatusChecker:
    def __init__(self, board: Board):
        self.board = board
        self.expected_number_of_walls = self.get_expected_number_of_walls()

    def get_expected_number_of_walls(self) -> int:
        total_number_of_cells = self.board.level.width_in_cells * self.board.level.height_in_cells
        expected_number_of_garden_cells = self.get_expected_number_of_garden_cells()
        return total_number_of_cells - expected_number_of_garden_cells

    def get_expected_number_of_garden_cells(self) -> int:
         return sum(cell.initial_value for cell in self.board.flat_cell_list if cell.initial_value is not None)

    def check_status(self, cell_change_info: CellChangeInfo) -> GameStatus:
        if not cell_change_info.is_wall_change():
            print('no wall changes')
            return GameStatus.IN_PROGRESS
        elif self.get_number_of_walls() != self.expected_number_of_walls:
            print('not correct number of walls')
            return GameStatus.IN_PROGRESS
        else:
            print('correct number of walls')


    def get_number_of_walls(self) -> int:
        return len([cell for cell in self.board.flat_cell_list if cell.cell_state is CellState.WALL])
