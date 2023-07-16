import pygame

from screen import Screen
from color import Color
from text_type import TextType
from pixel_position import PixelPosition


class Button:
    def __init__(self, screen: Screen, left: int, top: int, width: int, height: int, text: str,
                 is_clickable: bool = True):
        self.screen = screen
        self.text = text

        self.rect = pygame.Rect(left, top, width, height)
        self.is_clickable = is_clickable

        self.draw_button_rect()

    def draw_button_rect(self) -> None:
        # Background
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

        # Text and border
        color = Color.BLACK if self.is_clickable else Color.GRAY
        self.screen.draw_rect(color=color, rect=self.rect, width=1, text=self.text,
                              text_color=color, text_type=TextType.BUTTON)

    def is_inside_button(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def make_unclickable(self) -> None:
        self.is_clickable = False
        self.draw_button_rect()

    def make_clickable(self) -> None:
        self.is_clickable = True
        self.draw_button_rect()
