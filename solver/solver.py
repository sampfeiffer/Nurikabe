from screen import Screen
from board import Board
from cell import Cell
from cell_state import CellState


class Solver:
    def __init__(self, screen: Screen, board: Board):
        self.screen = screen
        self.board = board

    def run_solver(self) -> None:
        self.surround_ones()
        self.separate_clues()
        self.ensure_non_isolated_walls()

        self.board.update_painted_gardens()
        self.screen.update_screen()

    @staticmethod
    def set_cell_to_state(cell: Cell, target_cell_state: CellState) -> None:
        if not cell.is_clickable:
            raise RuntimeError(f'cell is not clickable: {cell}')
        cell.update_cell_state(target_cell_state)

    def surround_ones(self) -> None:
        cells_with_clue_of_1 = [cell for cell in self.board.flat_cell_list if cell.has_clue and cell.clue == 1]
        for cell in cells_with_clue_of_1:
            for adjacent_cell in cell.get_adjacent_neighbors():
                if adjacent_cell.is_clickable:
                    self.set_cell_to_state(adjacent_cell, CellState.WALL)

    def separate_clues(self) -> None:
        non_clue_cells = [cell for cell in self.board.flat_cell_list if not cell.has_clue]
        for cell in non_clue_cells:
            if len([cell for adjacent_cell in cell.get_adjacent_neighbors() if adjacent_cell.has_clue]) > 1:
                self.set_cell_to_state(cell, CellState.WALL)

    def ensure_non_isolated_walls(self) -> None:
        wall_sections = self.board.get_all_wall_sections()
        # TODO -  first ensure that there needs to be an "escape" for the wall section
        for wall_section in wall_sections:
            escape_routes = wall_section.get_escape_routes()
            if len(escape_routes) == 1:
                only_escape_route = escape_routes[0]
                self.set_cell_to_state(only_escape_route, CellState.WALL)
