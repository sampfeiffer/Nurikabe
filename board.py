import pygame

from screen import Screen
from level import Level
from cell import Cell
from position import Position


class Board:
    def __init__(self, screen: Screen, level: Level):
        self.screen = screen
        self.level = level

        self.rect = self.get_board_rect()
        self.draw_board_rect()
        self.cells = self.create_cells()

    def get_board_rect(self) -> pygame.Rect:
        top_left_of_board = self.get_top_left_of_board()
        width = self.screen.cell_width * self.level.width_in_cells
        height = self.screen.cell_width * self.level.height_in_cells
        return pygame.Rect(top_left_of_board.x_coordinate, top_left_of_board.y_coordinate, width, height)

    def get_top_left_of_board(self) -> Position:
        left_border_size = self.get_actual_left_border_size()
        return Position(left_border_size, Screen.MIN_BORDER)

    def get_actual_left_border_size(self) -> int:
        actual_board_width = self.screen.cell_width * self.level.width_in_cells
        return int((self.screen.SCREEN_WIDTH - actual_board_width) / 2)

    def draw_board_rect(self) -> None:
        pygame.draw.rect(surface=self.screen.screen, color=Screen.BOARD_COLOR, rect=self.rect)

    def create_cells(self) -> list[Cell]:
        cells: list[Cell] = []
        for row_number, row in enumerate(self.level.level_setup):
            for col_number, cell_value in enumerate(row):
                cell_location = self.screen.get_cell_location(self.rect, row_number, col_number)
                cells.append(Cell(row_number, col_number, cell_value, cell_location, self.screen))
        return cells

    def handle_board_click(self, event_position: Position) -> None:
        if not self.is_inside_board(event_position):
            return
        for cell in self.cells:
            if cell.is_inside_cell(event_position):
                cell.handle_cell_click()

    def is_inside_board(self, event_position: Position) -> bool:
        return self.rect.collidepoint(event_position.coordinates)
