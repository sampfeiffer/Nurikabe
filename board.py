from typing import Optional, Callable
import pygame

from screen import Screen
from level import Level
from cell import Cell
from pixel_position import PixelPosition
from color import Color
from cell_change_info import CellChangeInfo
from direction import Direction
from grid_coordinate import GridCoordinate


class Board:
    def __init__(self, screen: Screen, level: Level):
        self.screen = screen
        self.level = level

        self.rect = self.get_board_rect()
        self.draw_board_rect()
        self.cell_grid = self.create_cell_grid()
        self.flat_cell_list = self.get_flat_cell_list()
        self.set_cell_neighbors()

    def get_board_rect(self) -> pygame.Rect:
        top_left_of_board = self.get_top_left_of_board()
        width = self.screen.cell_width * self.level.width_in_cells
        height = self.screen.cell_width * self.level.height_in_cells
        return pygame.Rect(top_left_of_board.x_coordinate, top_left_of_board.y_coordinate, width, height)

    def get_top_left_of_board(self) -> PixelPosition:
        left_border_size = self.get_actual_left_border_size()
        return PixelPosition(left_border_size, Screen.MIN_BORDER)

    def get_actual_left_border_size(self) -> int:
        actual_board_width = self.screen.cell_width * self.level.width_in_cells
        return int((self.screen.SCREEN_WIDTH - actual_board_width) / 2)

    def draw_board_rect(self) -> None:
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

    def create_cell_grid(self) -> list[list[Cell]]:
        return [[self.create_cell(row_number, col_number, cell_value) for col_number, cell_value in enumerate(row)]
                for row_number, row in enumerate(self.level.level_setup)]

    def create_cell(self, row_number: int, col_number: int, cell_value: Optional[int]) -> Cell:
        cell_pixel_position = self.screen.get_cell_location(self.rect, row_number, col_number)
        return Cell(row_number, col_number, cell_value, cell_pixel_position, self.screen)

    def get_flat_cell_list(self) -> list[Cell]:
        return [cell for row in self.cell_grid for cell in row]

    def get_cell_from_grid(self, row_number: int, col_number: int) -> Cell:
        return self.cell_grid[row_number][col_number]

    def set_cell_neighbors(self) -> None:
        for cell in self.flat_cell_list:
            neighbor_cell_map: dict[Direction, Cell] = {}
            for direction in Direction:
                neighbor_cell = self.get_neighbor_cell(cell, direction)
                if neighbor_cell is not None:
                    neighbor_cell_map[direction] = neighbor_cell
            cell.set_neighbor_map(neighbor_cell_map)

    def get_neighbor_cell(self, cell: Cell, direction: Direction) -> Optional[Cell]:
        neighbor_coordinate = cell.grid_coordinate.get_offset(direction)
        if self.is_valid_cell_coordinate(neighbor_coordinate):
            return self.get_cell_from_grid(row_number=neighbor_coordinate.row_number,
                                           col_number=neighbor_coordinate.col_number)

    def is_valid_cell_coordinate(self, grid_coordinate: GridCoordinate) -> bool:
        return 0 <= grid_coordinate.row_number < self.level.height_in_cells and \
            0 <= grid_coordinate.col_number < self.level.width_in_cells

    def handle_board_click(self, event_position: PixelPosition) -> Optional[CellChangeInfo]:
        if not self.is_inside_board(event_position):
            return
        for cell in self.flat_cell_list:
            if cell.is_inside_cell(event_position):
                return cell.handle_cell_click()

    def is_inside_board(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def get_connected_cells(self, starting_cell: Cell, cell_criteria_func: Callable[[Cell], bool],
                            connected_cells: Optional[set[Cell]] = None) -> set[Cell]:
        """
        Get a list of cells that are connected (non-diagonally) to the starting cell where the cell_criteria_func
        returns True.
        """
        if connected_cells is None:
            connected_cells = set()
        if starting_cell in connected_cells:
            # Already visited this cell
            return connected_cells
        if cell_criteria_func(starting_cell):
            connected_cells.add(starting_cell)
            for neighbor_cell in starting_cell.get_adjacent_neighbors():
                self.get_connected_cells(neighbor_cell, cell_criteria_func, connected_cells)

        return connected_cells

    def get_all_gardens(self) -> list[set[Cell]]:
        gardens: list[set[Cell]] = []
        cells_in_gardens: set[Cell] = set()  # to prevent double counting
        for cell in self.flat_cell_list:
            if cell in cells_in_gardens or cell.cell_state.is_wall():
                continue
            garden = self.get_garden(starting_cell=cell)
            gardens.append(garden)
            cells_in_gardens = cells_in_gardens.union(garden)
        return gardens

    def get_garden(self, starting_cell: Cell) -> set[Cell]:
        return self.get_connected_cells(starting_cell, cell_criteria_func=lambda cell: not cell.cell_state.is_wall())
