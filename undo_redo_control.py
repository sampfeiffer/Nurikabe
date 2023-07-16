from screen import Screen
from board import Board
from button import Button
from pixel_position import PixelPosition
from cell_change_info import CellChanges


class UndoRedoControl:
    def __init__(self, screen: Screen, board: Board):
        self.board = board

        self.undo_button = UndoButton(screen, board)
        self.redo_button = RedoButton(screen, board)
        self.buttons = (self.undo_button, self.redo_button)

        self.undo_stack: list[CellChanges] = []
        self.redo_stack: list[CellChanges] = []

    def process_board_event(self, cell_changes: CellChanges) -> None:
        self.undo_stack.append(cell_changes)
        self.redo_stack.clear()

    def process_potential_button_click(self, event_position: PixelPosition) -> None:
        if self.should_run_undo(event_position):
            self.handle_undo()
        elif self.should_run_redo(event_position):
            self.handle_redo()

    def should_run_undo(self, event_position: PixelPosition) -> bool:
        return self.undo_button.is_clickable and self.undo_button.is_inside_button(event_position)

    def should_run_redo(self, event_position: PixelPosition) -> bool:
        return self.redo_button.is_clickable and self.redo_button.is_inside_button(event_position)

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

    def make_unclickable(self) -> None:
        for button in self.buttons:
            button.make_unclickable()


class UndoButton(Button):
    def __init__(self, screen: Screen, board: Board):
        left = self.get_left_coordinate(board)
        top = board.rect.bottom + screen.MIN_BORDER
        super().__init__(screen, left, top, width=Screen.UNDO_REDO_BUTTON_RECT_WIDTH,
                         height=Screen.BUTTON_RECT_HEIGHT, text='Undo')

    @staticmethod
    def get_left_coordinate(board: Board) -> int:
        return board.rect.left


class RedoButton(Button):
    def __init__(self, screen: Screen, board: Board):
        left = self.get_left_coordinate(board)
        top = board.rect.bottom + screen.MIN_BORDER
        super().__init__(screen, left, top, width=Screen.UNDO_REDO_BUTTON_RECT_WIDTH,
                         height=Screen.BUTTON_RECT_HEIGHT, text='Redo')

    @staticmethod
    def get_left_coordinate(board: Board) -> int:
        return board.rect.left + Screen.UNDO_REDO_BUTTON_RECT_WIDTH + Screen.MIN_BORDER
