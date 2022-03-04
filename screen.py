from typing import Optional
import pygame

from level import Level
from pixel_position import PixelPosition
from color import Color


class Screen:
    SCREEN_WIDTH = 300
    SCREEN_HEIGHT = 500
    MIN_BORDER = 5

    def __init__(self, level: Level):
        self.screen = pygame.display.set_mode(size=(Screen.SCREEN_WIDTH, Screen.SCREEN_HEIGHT))
        pygame.display.set_caption('Nurikabe')
        self.screen.fill(Color.GRAY.value)

        self.cell_width = self.get_cell_width(level.width_in_cells, level.height_in_cells)
        self.font = self.get_font()

    def get_cell_width(self, width_in_cells: int, height_in_cells: int) -> int:
        max_board_width = self.SCREEN_WIDTH - 2 * self.MIN_BORDER
        max_cell_width = int(max_board_width / width_in_cells)

        max_board_height = self.SCREEN_HEIGHT - 2 * self.MIN_BORDER
        max_cell_height = int(max_board_height / height_in_cells)

        return min((max_cell_width, max_cell_height))

    def get_font(self) -> pygame.font.SysFont:
        font_size = self.get_font_size()
        return pygame.font.SysFont('Courier', font_size)

    def get_font_size(self) -> int:
        return int(0.8 * self.cell_width)

    def get_cell_location(self, board_rect: pygame.Rect, row_number: int, col_number: int) -> PixelPosition:
        left = board_rect.left + self.cell_width * col_number
        top = board_rect.top + self.cell_width * row_number
        return PixelPosition(left, top)

    def draw_rect(self, color: Color, rect: pygame.Rect, width: int, text: Optional[str] = None,
                  text_color: Optional[Color] = None) -> None:
        pygame.draw.rect(surface=self.screen, color=color.value, rect=rect, width=width)
        if text is not None:
            if text_color is None:
                raise RuntimeError('text_color must be provided if text is provided')
            text = self.font.render(text, True, text_color.value)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    @staticmethod
    def update_screen() -> None:
        pygame.display.flip()
