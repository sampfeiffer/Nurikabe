import sys
import logging
import pygame

from screen import Screen
from level import Level
from board import Board
from position import Position

logger = logging.getLogger(__name__)

LEFT_BUTTON = 1


class Nurikabe:
    def __init__(self, level_number: int):
        level = Level(level_number)
        self.screen = Screen(level)
        self.board = Board(self.screen, level)
        self.start_game_loop()

    def start_game_loop(self) -> None:
        while True:
            self.process_event_queue()
            pygame.time.wait(20)  # milliseconds
            self.screen.update_screen()

    def process_event_queue(self) -> None:
        for event in pygame.event.get():
            self.process_single_event(event)

    def process_single_event(self, event: pygame.event.Event) -> None:
        event_type = event.type
        if event_type == pygame.QUIT:
            self.process_quit()
        elif event_type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
            event_position = Position.from_tuple(event.pos)
            self.process_left_click_down(event_position)
        else:
            pass  # ignore all other events

    @staticmethod
    def process_quit() -> None:
        logger.info('exiting')
        sys.exit()

    def process_left_click_down(self, event_position: Position) -> None:
        self.board.handle_board_click(event_position)
