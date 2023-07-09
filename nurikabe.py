import sys
import logging
from typing import Optional
import pygame

from screen import Screen
from level import Level
from board import Board
from pixel_position import PixelPosition
from game_status_checker import GameStatusChecker
from game_status import GameStatus
from solver_button_display import SolverButtonDisplay
from game_status_display import GameStatusDisplay
from cell_change_info import CellChangeInfo
from solver.solver import Solver

logger = logging.getLogger(__name__)

LEFT_BUTTON = 1  # Pygame's representation of a left button click


class Nurikabe:
    def __init__(self, level_number: int, should_use_solver: bool, should_include_grid_numbers: bool):
        level = Level(level_number)
        self.screen = Screen(level, should_include_grid_numbers)
        self.board = Board(level, self.screen)
        self.solver_button_display = SolverButtonDisplay(self.screen, self.board, should_use_solver)
        self.game_status_display = GameStatusDisplay(self.screen)
        self.game_status_checker = GameStatusChecker(self.board)
        self.should_use_solver = should_use_solver
        self.solver = Solver(self.screen, self.board)
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
            event_position = PixelPosition.from_tuple(event.pos)
            self.process_left_click_down(event_position)
        else:
            pass  # ignore all other events

    @staticmethod
    def process_quit() -> None:
        logger.info('exiting')
        sys.exit()

    def process_left_click_down(self, event_position: PixelPosition) -> None:
        if self.solver_button_display.should_run_solver(event_position):
            self.solver.run_solver()
            self.check_game_status()
        cell_change_info = self.board.handle_board_click(event_position)
        self.screen.update_screen()
        if cell_change_info is not None:
            self.check_game_status(cell_change_info)

    def check_game_status(self, cell_change_info: Optional[CellChangeInfo] = None) -> None:
        game_status = self.game_status_checker.is_solution_correct(cell_change_info)
        if game_status is GameStatus.PUZZLE_SOLVED:
            self.handle_solved_puzzle()

    def handle_solved_puzzle(self) -> None:
        self.game_status_display.show_puzzle_solved_message()
        self.board.freeze_cells()
        self.solver_button_display.make_unclickable()
