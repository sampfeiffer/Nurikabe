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
        self.is_mouse_on_button = False
        self.is_left_mouse_down = False

        self.draw_button_rect()

    def draw_button_rect(self) -> None:
        # Background
        self.screen.draw_rect(color=self.get_background_color(), rect=self.rect, width=0)

        # Text and border
        color = Color.BLACK if self.is_clickable else Color.GRAY
        self.screen.draw_rect(color=color, rect=self.rect, width=1, text=self.text,
                              text_color=color, text_type=TextType.BUTTON)

    def get_background_color(self) -> Color:
        if not self.is_clickable or not self.is_mouse_on_button:
            color = Color.OFF_WHITE
        else:
            if self.is_left_mouse_down:
                color = Color.MEDIUM_SLATE_GRAY
            else:
                color = Color.LIGHT_SLATE_GRAY
        return color

    def process_potential_left_click_down(self, event_position: PixelPosition) -> None:
        if self.should_handle_mouse_event(event_position):
            self.handle_left_click_down()

    def should_handle_mouse_event(self, event_position: PixelPosition) -> bool:
        return self.is_clickable and self.is_inside_button(event_position)

    def handle_left_click_down(self) -> None:
        self.is_left_mouse_down = True
        self.draw_button_rect()

    def process_potential_left_click_up(self, event_position: PixelPosition) -> None:
        if self.should_handle_mouse_event(event_position):
            self.handle_left_click_up()

    def handle_left_click_up(self) -> None:
        self.is_left_mouse_down = False
        self.draw_button_rect()

    def process_mouse_motion(self, event_position: PixelPosition, is_left_mouse_down: bool) -> None:
        if self.should_handle_mouse_event(event_position):
            self.handle_mouse_motion(is_left_mouse_down)
        elif self.is_mouse_on_button:
            self.is_mouse_on_button = False
            self.is_left_mouse_down = False
            self.draw_button_rect()

    def handle_mouse_motion(self, is_left_mouse_down: bool) -> None:
        if not self.is_mouse_on_button or self.is_left_mouse_down != is_left_mouse_down:
            self.is_mouse_on_button = True
            self.is_left_mouse_down = is_left_mouse_down
            self.draw_button_rect()

    def is_inside_button(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def make_unclickable(self) -> None:
        self.is_clickable = False
        self.draw_button_rect()

    def make_clickable(self) -> None:
        self.is_clickable = True
        self.draw_button_rect()
