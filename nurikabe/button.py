import pygame

from .color import Color
from .pixel_position import PixelPosition
from .screen import Screen
from .text_type import TextType


class Button:
    ENABLED_TEXT_COLOR = Color.BLACK
    DISABLED_TEXT_COLOR = Color.GRAY

    def __init__(  # noqa: PLR0913
        self,
        screen: Screen,
        left: int,
        top: int,
        width: int,
        height: int,
        text: str | None = None,
        image: pygame.Surface | None = None,
        *,
        is_clickable: bool = True,
    ):
        self.screen = screen
        self.text = text
        self.image = image
        self.image_disabled = self.get_disabled_button_image()

        if self.text is not None and self.image is not None:
            msg = 'Button cannot have both text and an image'
            raise ValueError(msg)

        self.rect = pygame.Rect(left, top, width, height)
        self.is_clickable = is_clickable
        self.is_mouse_on_button = False
        self.is_left_mouse_down = False

        self.draw_button_rect()

    def get_disabled_button_image(self) -> pygame.Surface | None:
        if self.image is None:
            disabled_image = None
        else:
            disabled_image = self.image.copy()
            disabled_image.set_alpha(255 - Button.DISABLED_TEXT_COLOR.value[0])
        return disabled_image

    def draw_button_rect(self) -> None:
        # Background
        self.screen.draw_rect(color=self.get_background_color(), rect=self.rect, width=0)

        # Text and border
        if self.is_clickable:
            color = Button.ENABLED_TEXT_COLOR
            image = self.image
        else:
            color = Button.DISABLED_TEXT_COLOR
            image = self.image_disabled
        self.screen.draw_rect(
            color=color,
            rect=self.rect,
            width=1,
            text=self.text,
            text_color=color,
            text_type=TextType.BUTTON,
            image=image,
        )

    def get_background_color(self) -> Color:
        if not self.is_clickable or not self.is_mouse_on_button:
            color = Color.OFF_WHITE
        else:
            color = Color.MEDIUM_SLATE_GRAY if self.is_left_mouse_down else Color.LIGHT_SLATE_GRAY
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

    def process_mouse_motion(self, event_position: PixelPosition, *, is_left_mouse_down: bool) -> None:
        if self.should_handle_mouse_event(event_position):
            self.handle_mouse_motion(is_left_mouse_down=is_left_mouse_down)
        elif self.is_mouse_on_button:
            self.is_mouse_on_button = False
            self.is_left_mouse_down = False
            self.draw_button_rect()

    def handle_mouse_motion(self, *, is_left_mouse_down: bool) -> None:
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
