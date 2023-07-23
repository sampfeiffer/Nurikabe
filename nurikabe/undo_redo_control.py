from pathlib import Path
import pygame

from .screen import Screen
from .board import Board
from .button import Button
from .pixel_position import PixelPosition
from .cell_change_info import CellChanges


class UndoRedoControl:
    def __init__(self, screen: Screen, board: Board):
        self.board = board

        self.undo_button = UndoButton(screen, board)
        self.redo_button = RedoButton(screen, board)
        self.buttons = (self.undo_button, self.redo_button)

        self.undo_stack: list[CellChanges] = []
        self.redo_stack: list[CellChanges] = []

    def process_board_event(self, cell_changes: CellChanges) -> None:
        if cell_changes.has_any_changes():
            self.undo_stack.append(cell_changes)
            self.redo_stack.clear()
            self.undo_button.make_clickable()
            self.redo_button.make_unclickable()

    def process_potential_left_click_up(self, event_position: PixelPosition) -> None:
        if self.undo_button.should_handle_mouse_event(event_position):
            self.undo_button.handle_left_click_up()
            self.handle_undo()
        elif self.redo_button.should_handle_mouse_event(event_position):
            self.redo_button.handle_left_click_up()
            self.handle_redo()

        self.set_button_status()

    def handle_undo(self) -> None:
        if len(self.undo_stack) > 0:
            most_recent_cell_changes = self.undo_stack.pop()
            self.redo_stack.append(most_recent_cell_changes)
            reversed_cell_changes = most_recent_cell_changes.get_reversed_changes()
            self.board.apply_cell_changes(reversed_cell_changes)
            self.board.update_painted_gardens()

    def handle_redo(self) -> None:
        if len(self.redo_stack) > 0:
            cell_changes = self.redo_stack.pop()
            self.undo_stack.append(cell_changes)
            self.board.apply_cell_changes(cell_changes)
            self.board.update_painted_gardens()

    def set_button_status(self) -> None:
        if len(self.undo_stack) > 0:
            self.undo_button.make_clickable()
        else:
            self.undo_button.make_unclickable()

        if len(self.redo_stack) > 0:
            self.redo_button.make_clickable()
        else:
            self.redo_button.make_unclickable()


class UndoButton(Button):
    def __init__(self, screen: Screen, board: Board):
        left = self.get_left_coordinate(board)
        top = board.rect.bottom + screen.MIN_BORDER
        super().__init__(screen, left, top, width=Screen.UNDO_REDO_BUTTON_RECT_WIDTH,
                         height=Screen.BUTTON_RECT_HEIGHT, image=self.get_image(), is_clickable=False)

    @staticmethod
    def get_left_coordinate(board: Board) -> int:
        return board.rect.left

    @staticmethod
    def get_image() -> pygame.Surface:
        undo_image = pygame.image.load(Path(__file__).parent / 'icons/undo.png').convert_alpha()
        image_square_length = Screen.BUTTON_RECT_HEIGHT - 4
        return pygame.transform.smoothscale(undo_image, (image_square_length, image_square_length))


class RedoButton(Button):
    def __init__(self, screen: Screen, board: Board):
        left = self.get_left_coordinate(board)
        top = board.rect.bottom + screen.MIN_BORDER
        super().__init__(screen, left, top, width=Screen.UNDO_REDO_BUTTON_RECT_WIDTH,
                         height=Screen.BUTTON_RECT_HEIGHT, image=self.get_image(), is_clickable=False)

    @staticmethod
    def get_left_coordinate(board: Board) -> int:
        return board.rect.left + Screen.UNDO_REDO_BUTTON_RECT_WIDTH + Screen.MIN_BORDER

    @staticmethod
    def get_image() -> pygame.Surface:
        redo_image = pygame.image.load(Path(__file__).parent / 'icons/redo.png').convert_alpha()
        image_square_length = Screen.BUTTON_RECT_HEIGHT - 4
        return pygame.transform.smoothscale(redo_image, (image_square_length, image_square_length))
