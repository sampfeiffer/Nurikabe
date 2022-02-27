from typing import Optional
import pygame

from screen import Screen
from cell_state import CellState
from position import Position
from color import Color
from cell_change_info import CellChangeInfo


class Cell:
    CENTER_DOT = '\u2022'

    def __init__(self, row_number: int, col_number: int, initial_value: Optional[int], cell_location: Position,
                 screen: Screen):
        self.row_number = row_number
        self.col_number = col_number
        self.initial_value = initial_value
        self.cell_location = cell_location
        self.screen = screen

        self.is_clickable = self.initial_value is None
        self.cell_state = CellState.EMPTY

        self.rect = self.get_rect()
        self.draw_initial_value()

    def get_rect(self) -> pygame.Rect:
        width = self.screen.cell_width
        height = self.screen.cell_width
        return pygame.Rect(self.cell_location.x_coordinate, self.cell_location.y_coordinate, width, height)

    def draw_initial_value(self) -> None:
        text = None if self.initial_value is None else str(self.initial_value)
        self.draw_empty_cell(text)

    def draw_empty_cell(self, text: Optional[str] = None) -> None:
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)  # background
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=1, text=text)  # border (and text if provided)

    def draw_wall_cell(self) -> None:
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=0)

    def draw_non_wall_cell(self) -> None:
        self.draw_empty_cell(text=self.CENTER_DOT)

    def is_inside_cell(self, event_position: Position) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def handle_cell_click(self) -> Optional[CellChangeInfo]:
        if not self.is_clickable:
            return

        new_cell_state = self.cell_state.get_next_in_cycle()
        return self.update_cell_state(new_cell_state)

    def update_cell_state(self, new_cell_state: CellState) -> Optional[CellChangeInfo]:
        if new_cell_state is CellState.EMPTY:
            self.draw_empty_cell()
        elif new_cell_state is CellState.WALL:
            self.draw_wall_cell()
        elif new_cell_state is CellState.NON_WALL:
            self.draw_non_wall_cell()
        else:
            raise RuntimeError('This should not be possible')
        cell_change_info = CellChangeInfo(before_state=self.cell_state, after_state=new_cell_state)
        self.cell_state = new_cell_state
        return cell_change_info
