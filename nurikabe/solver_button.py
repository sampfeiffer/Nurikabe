from .screen import Screen
from .board import Board
from .button import Button


class SolverButton(Button):
    def __init__(self, screen: Screen, board: Board):
        left = self.get_left_coordinate(board)
        top = board.rect.bottom + screen.MIN_BORDER
        super().__init__(screen, left, top, width=Screen.SOLVER_BUTTON_RECT_WIDTH,
                         height=Screen.BUTTON_RECT_HEIGHT, text='Run solver iteration')

    @staticmethod
    def get_left_coordinate(board: Board) -> int:
        return board.rect.left + Screen.UNDO_REDO_BUTTON_RECT_WIDTH + Screen.MIN_BORDER + \
            Screen.UNDO_REDO_BUTTON_RECT_WIDTH + Screen.MIN_BORDER
