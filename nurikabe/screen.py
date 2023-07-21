from typing import Optional
import pygame

from level import Level
from pixel_position import PixelPosition
from color import Color
from text_type import TextType


class Screen:
    SCREEN_WIDTH = 450
    SCREEN_HEIGHT = 750
    MIN_BORDER = 5
    SHOULD_APPLY_ANTI_ALIAS = True

    BUTTON_RECT_HEIGHT = 22
    BUTTON_FONT_SIZE = 12
    UNDO_REDO_BUTTON_RECT_WIDTH = BUTTON_RECT_HEIGHT
    SOLVER_BUTTON_RECT_WIDTH = 150
    SPACE_BETWEEN_BUTTONS = 5

    GRID_NUMBERING_WIDTH = 25
    GRID_NUMBERING_MIN_FONT_SIZE = 7
    GRID_NUMBERING_MAX_FONT_SIZE = 20

    GAME_STATUS_RECT_WIDTH = int(0.75 * SCREEN_WIDTH)
    GAME_STATUS_RECT_HEIGHT = 30
    PUZZLE_SOLVED_FONT_SIZE = 25
    FONT = 'Courier'

    BACKGROUND_COLOR = Color.GRAY

    def __init__(self, level: Level, should_include_grid_numbers: bool):
        self.screen = pygame.display.set_mode(size=(Screen.SCREEN_WIDTH, Screen.SCREEN_HEIGHT))
        pygame.display.set_caption('Nurikabe')
        self.screen.fill(Screen.BACKGROUND_COLOR.value)

        self.top_left_of_game_status = self.get_top_left_of_game_status()
        self.cell_width = self.get_cell_width(level.number_of_rows, level.number_of_columns,
                                              should_include_grid_numbers)
        self.top_left_of_board = self.get_top_left_of_board(should_include_grid_numbers)

        self.font_map = {
            TextType.CELL: self.get_cell_font(),
            TextType.PUZZLE_SOLVED: pygame.font.SysFont(self.FONT, self.PUZZLE_SOLVED_FONT_SIZE),
            TextType.BUTTON: pygame.font.SysFont(self.FONT, self.BUTTON_FONT_SIZE),
            TextType.GRID_NUMBERING: self.get_grid_numbering_font()
        }

        if should_include_grid_numbers:
            self.display_grid_numbering(level)

    def get_top_left_of_game_status(self) -> PixelPosition:
        left = int((self.SCREEN_WIDTH - self.GAME_STATUS_RECT_WIDTH) / 2)
        top = self.SCREEN_HEIGHT - (self.GAME_STATUS_RECT_HEIGHT + self.MIN_BORDER)
        return PixelPosition(x_coordinate=left, y_coordinate=top)

    def get_cell_width(self, number_of_rows: int, number_of_columns: int, should_include_grid_numbers: bool) -> int:
        width_for_non_board_components = self.get_left_side_of_board_width(should_include_grid_numbers) + \
            self.get_right_side_of_board_width()
        max_board_width = self.SCREEN_WIDTH - width_for_non_board_components
        max_cell_width = int(max_board_width / number_of_columns)

        height_for_non_board_components = self.get_top_of_board_height(should_include_grid_numbers) + \
            self.get_bottom_of_board_height()
        max_board_height = self.SCREEN_HEIGHT - height_for_non_board_components
        max_cell_height = int(max_board_height / number_of_rows)

        return min((max_cell_width, max_cell_height))

    def get_left_side_of_board_width(self, should_include_grid_numbers: bool) -> int:
        left_side_of_board_width = self.MIN_BORDER
        if should_include_grid_numbers:
            left_side_of_board_width += self.GRID_NUMBERING_WIDTH
        return left_side_of_board_width

    def get_right_side_of_board_width(self) -> int:
        return self.MIN_BORDER

    def get_top_of_board_height(self, should_include_grid_numbers: bool) -> int:
        top_of_board_height = self.MIN_BORDER
        if should_include_grid_numbers:
            top_of_board_height += self.GRID_NUMBERING_WIDTH
        return top_of_board_height

    def get_bottom_of_board_height(self) -> int:
        return self.MIN_BORDER + self.GAME_STATUS_RECT_HEIGHT + self.BUTTON_RECT_HEIGHT

    def get_top_left_of_board(self, should_include_grid_numbers: bool) -> PixelPosition:
        left_border_size = self.get_left_side_of_board_width(should_include_grid_numbers)
        top_border_size = self.get_top_of_board_height(should_include_grid_numbers)
        return PixelPosition(x_coordinate=left_border_size, y_coordinate=top_border_size)

    def get_cell_font(self) -> pygame.font.SysFont:
        font_size = self.get_cell_font_size()
        return pygame.font.SysFont(self.FONT, font_size)

    def get_cell_font_size(self) -> int:
        return int(0.8 * self.cell_width)

    def get_grid_numbering_font(self) -> pygame.font.SysFont:
        font_size = self.get_grid_numbering_font_size()
        return pygame.font.SysFont(self.FONT, font_size)

    def get_grid_numbering_font_size(self) -> int:
        font_size = int(0.5 * self.get_cell_font_size())
        return max(min(font_size, Screen.GRID_NUMBERING_MAX_FONT_SIZE), Screen.GRID_NUMBERING_MIN_FONT_SIZE)

    def display_grid_numbering(self, level: Level) -> None:
        for row_number in range(level.number_of_rows):
            row_label_rect = self.get_row_label_rect(row_number)
            self.draw_rect(color=Screen.BACKGROUND_COLOR, rect=row_label_rect, width=0, text=str(row_number),
                           text_color=Color.BLACK, text_type=TextType.GRID_NUMBERING)
        for column_number in range(level.number_of_columns):
            row_label_rect = self.get_column_label_rect(column_number)
            self.draw_rect(color=Screen.BACKGROUND_COLOR, rect=row_label_rect, width=0, text=str(column_number),
                           text_color=Color.BLACK, text_type=TextType.GRID_NUMBERING)

    def get_row_label_rect(self, row_number: int) -> pygame.Rect:
        left = self.top_left_of_board.x_coordinate - self.GRID_NUMBERING_WIDTH
        top = self.top_left_of_board.y_coordinate + self.cell_width * row_number
        width = self.GRID_NUMBERING_WIDTH
        height = self.cell_width
        return pygame.Rect(left, top, width, height)

    def get_column_label_rect(self, column_number: int) -> pygame.Rect:
        left = self.top_left_of_board.x_coordinate + self.cell_width * column_number
        top = self.top_left_of_board.y_coordinate - self.GRID_NUMBERING_WIDTH
        width = self.cell_width
        height = self.GRID_NUMBERING_WIDTH
        return pygame.Rect(left, top, width, height)

    def get_cell_location(self, board_rect: pygame.Rect, row_number: int, col_number: int) -> PixelPosition:
        left = board_rect.left + self.cell_width * col_number
        top = board_rect.top + self.cell_width * row_number
        return PixelPosition(x_coordinate=left, y_coordinate=top)

    def draw_rect(self, color: Color, rect: pygame.Rect, width: int, text: Optional[str] = None,
                  text_color: Optional[Color] = None, text_type: TextType = TextType.CELL,
                  image: Optional[pygame.Surface] = None) -> None:

        if text is not None and image is not None:
            raise ValueError('Cannot have both text and an image')

        pygame.draw.rect(surface=self.screen, color=color.value, rect=rect, width=width)
        if text is not None:
            if text_color is None:
                raise RuntimeError('text_color must be provided if text is provided')
            font = self.font_map[text_type]
            text = font.render(text, self.SHOULD_APPLY_ANTI_ALIAS, text_color.value)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        if image is not None:
            image_rect = image.get_rect(center=rect.center)
            self.screen.blit(image, dest=image_rect.topleft)

    @staticmethod
    def update_screen() -> None:
        pygame.display.flip()
