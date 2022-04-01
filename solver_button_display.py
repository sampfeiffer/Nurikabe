import pygame

from screen import Screen
from board import Board
from color import Color
from text_type import TextType
from pixel_position import PixelPosition


class SolverButtonDisplay:
    BUTTON_TEXT = 'Run solver iteration'

    def __init__(self, screen: Screen, board: Board, should_use_solver: bool):
        self.screen = screen
        self.board = board
        self.should_use_solver = should_use_solver

        self.rect = self.get_display_rect()
        if self.should_use_solver:
            self.is_button_clickable = True
            self.draw_button_rect()
        else:
            self.is_button_clickable = False

    def get_display_rect(self) -> pygame.Rect:
        left = self.board.rect.left
        top = self.board.rect.bottom + self.screen.MIN_BORDER
        return pygame.Rect(left, top, self.screen.SOLVER_BUTTON_RECT_WIDTH, self.screen.SOLVER_BUTTON_RECT_HEIGHT)

    def draw_button_rect(self) -> None:
        # Background
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

        # Text and border
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=1, text=self.BUTTON_TEXT,
                              text_color=Color.BLACK, text_type=TextType.SOLVER_BUTTON)

    def should_run_solver(self, event_position: PixelPosition) -> bool:
        return self.is_button_clickable and self.is_inside_button(event_position)

    def is_inside_button(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def make_unclickable(self) -> None:
        self.is_button_clickable = False
