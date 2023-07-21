import pygame

from .screen import Screen
from .color import Color
from .text_type import TextType


class GameStatusDisplay:
    PUZZLE_SOLVED_MESSAGE = 'Puzzle Solved!'

    def __init__(self, screen: Screen):
        self.screen = screen

        self.rect = self.get_display_rect()

    def get_display_rect(self) -> pygame.Rect:
        location = self.screen.top_left_of_game_status
        return pygame.Rect(location.x_coordinate, location.y_coordinate, self.screen.GAME_STATUS_RECT_WIDTH,
                           self.screen.GAME_STATUS_RECT_HEIGHT)

    def show_puzzle_solved_message(self) -> None:
        self.screen.draw_rect(color=Color.GRAY, rect=self.rect, width=0, text=self.PUZZLE_SOLVED_MESSAGE,
                              text_color=Color.BLACK, text_type=TextType.PUZZLE_SOLVED)
