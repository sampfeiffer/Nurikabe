from board import Board
from game_status import GameStatus
from cell_change_info import CellChangeInfo


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

    def is_solution_correct(self, cell_change_info: CellChangeInfo) -> GameStatus:
        if not cell_change_info.is_wall_change():
            print('no wall changes')
            game_status = GameStatus.IN_PROGRESS
        elif not self.has_expected_number_of_walls():
            print('not correct number of walls')
            game_status = GameStatus.IN_PROGRESS
        elif self.has_two_by_two_wall():
            print('has two by two wall')
            game_status = GameStatus.IN_PROGRESS
        elif not self.do_gardens_have_exactly_one_clue():
            print('gardens must have exactly one clue')
            game_status = GameStatus.IN_PROGRESS
        elif not self.are_gardens_appropriately_sized():
            print('garden size must equal the clue value')
            game_status = GameStatus.IN_PROGRESS
        elif not self.are_all_walls_connected():
            print('walls are not all connected')
            game_status = GameStatus.IN_PROGRESS
        else:
            print('correct solution!')
            game_status = GameStatus.GAME_OVER

        return game_status

    def has_expected_number_of_walls(self) -> bool:
        return self.get_number_of_walls() == self.expected_number_of_walls

    def get_number_of_walls(self) -> int:
        return len([cell for cell in self.board.flat_cell_list if cell.cell_state.is_wall()])

    def has_two_by_two_wall(self) -> bool:
        pass

    def do_gardens_have_exactly_one_clue(self) -> bool:
        pass

    def are_gardens_appropriately_sized(self) -> bool:
        pass

    def are_all_walls_connected(self) -> bool:
        pass
