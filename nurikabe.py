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
from solver_button import SolverButton
from undo_redo_control import UndoRedoControl
from game_status_display import GameStatusDisplay
from cell_change_info import CellChangeInfo, CellChanges
from solver.solver import Solver
from button import Button

logger = logging.getLogger(__name__)

LEFT_MOUSE_BUTTON = 1  # Pygame's representation the left mouse button


class Nurikabe:
    def __init__(self, level_number: int, should_use_solver: bool, should_include_grid_numbers: bool):
        level = Level(level_number)
        self.screen = Screen(level, should_include_grid_numbers)
        self.board = Board(level, self.screen)
        self.undo_redo_control = UndoRedoControl(self.screen, self.board)
        self.buttons: list[Button] = list(self.undo_redo_control.buttons[::])

        self.should_use_solver = should_use_solver
        if self.should_use_solver:
            self.solver_button = SolverButton(self.screen, self.board)
            self.buttons.append(self.solver_button)

        self.game_status_display = GameStatusDisplay(self.screen)
        self.game_status_checker = GameStatusChecker(self.board)
        self.should_use_solver = should_use_solver
        self.solver = Solver(self.screen, self.board, self.undo_redo_control)
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
        elif event_type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_MOUSE_BUTTON:
            event_position = PixelPosition.from_tuple(event.pos)
            self.process_left_click_down(event_position)
        elif event_type == pygame.MOUSEBUTTONUP and event.button == LEFT_MOUSE_BUTTON:
            event_position = PixelPosition.from_tuple(event.pos)
            self.process_left_click_up(event_position)
        elif event_type == pygame.MOUSEMOTION:
            event_position = PixelPosition.from_tuple(event.pos)
            is_left_mouse_down = event.buttons[0] == 1
            self.process_mouse_motion(event_position, is_left_mouse_down)
        else:
            pass  # ignore all other events

    @staticmethod
    def process_quit() -> None:
        logger.info('exiting')
        sys.exit()

    def process_left_click_down(self, event_position: PixelPosition) -> None:
        for button in self.buttons:
            button.process_potential_left_click_down(event_position)

        cell_change_info = self.board.handle_board_click(event_position)
        if cell_change_info is not None:
            self.check_game_status(cell_change_info)
            self.undo_redo_control.process_board_event(CellChanges([cell_change_info]))
        self.screen.update_screen()

    def process_left_click_up(self, event_position: PixelPosition) -> None:
        self.undo_redo_control.process_potential_left_click_up(event_position)
        if self.should_use_solver and self.solver_button.should_handle_mouse_event(event_position):
            self.solver_button.handle_left_click_up()
            self.solver.run_solver()
            self.check_game_status()
        self.screen.update_screen()

    def process_mouse_motion(self, event_position: PixelPosition, is_left_mouse_down: bool) -> None:
        for button in self.buttons:
            button.process_mouse_motion(event_position, is_left_mouse_down)
        self.screen.update_screen()

    def check_game_status(self, cell_change_info: Optional[CellChangeInfo] = None) -> None:
        game_status = self.game_status_checker.is_solution_correct(cell_change_info)
        if game_status is GameStatus.PUZZLE_SOLVED:
            self.handle_solved_puzzle()

    def handle_solved_puzzle(self) -> None:
        self.game_status_display.show_puzzle_solved_message()
        self.board.freeze_cells()
        self.undo_redo_control.make_unclickable()
        if self.should_use_solver:
            self.solver_button.make_unclickable()
