import pygame

from screen import Screen
from color import Color
from text_type import TextType
from pixel_position import PixelPosition


class Button:
    def __init__(self, screen: Screen, left: int, top: int, width: int, height: int, text: str):
        self.screen = screen

        self.rect = pygame.Rect(left, top, width, height)
        self.is_clickable = True

        self.draw_button_rect(text)

    def draw_button_rect(self, text: str) -> None:
        # Background
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

        # Text and border
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=1, text=text,
                              text_color=Color.BLACK, text_type=TextType.BUTTON)

    def is_inside_button(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def make_unclickable(self) -> None:
        self.is_clickable = False
