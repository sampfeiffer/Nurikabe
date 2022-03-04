from __future__ import annotations
from typing import Optional, Iterable
import pygame

from screen import Screen
from cell_state import CellState
from pixel_position import PixelPosition
from color import Color
from cell_change_info import CellChangeInfo
from direction import Direction, ADJACENT_DIRECTIONS
from grid_coordinate import GridCoordinate


class NonExistentNeighbor(Exception):
    pass


class Cell:
    CENTER_DOT = '\u2022'

    def __init__(self, row_number: int, col_number: int, initial_value: Optional[int], pixel_position: PixelPosition,
                 screen: Screen):
        self.row_number = row_number
        self.col_number = col_number
        self.grid_coordinate = GridCoordinate(row_number, col_number)
        self.initial_value = initial_value
        self.screen = screen

        self.has_clue = self.initial_value is not None
        self.is_clickable = not self.has_clue
        self.cell_state = CellState.EMPTY

        self.rect = self.get_rect(pixel_position)
        self.draw_cell(is_in_completed_garden=False)

        self.neighbor_cell_map: Optional[dict[Direction, Cell]] = None

    def get_rect(self, pixel_position: PixelPosition) -> pygame.Rect:
        width = self.screen.cell_width
        height = self.screen.cell_width
        return pygame.Rect(pixel_position.x_coordinate, pixel_position.y_coordinate, width, height)

    def draw_cell(self, is_in_completed_garden: bool) -> None:
        if self.has_clue:
            self.draw_initial_value(is_in_completed_garden)
        elif self.cell_state is CellState.EMPTY:
            self.draw_garden_cell()
        elif self.cell_state is CellState.WALL:
            self.draw_wall_cell()
        elif self.cell_state is CellState.NON_WALL:
            self.draw_non_wall_cell(is_in_completed_garden)
        else:
            raise RuntimeError('This should not be possible')

    def draw_initial_value(self, is_in_completed_garden: bool) -> None:
        text = None if self.initial_value is None else str(self.initial_value)
        self.draw_garden_cell(text, is_in_completed_garden)

    def draw_garden_cell(self, text: Optional[str] = None, is_in_completed_garden: Optional[bool] = None) -> None:
        if text is not None and is_in_completed_garden is None:
            raise RuntimeError('is_in_completed_garden must be provided if text is provided')

        # background
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

        # border (and text if provided)
        text_color = Color.GRAY if is_in_completed_garden else Color.BLACK
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=1, text=text, text_color=text_color)

    def draw_wall_cell(self) -> None:
        self.screen.draw_rect(color=Color.BLACK, rect=self.rect, width=0)

    def draw_non_wall_cell(self, is_in_completed_garden: bool) -> None:
        text = self.CENTER_DOT
        self.draw_garden_cell(text, is_in_completed_garden)

    def paint_completed_cell(self) -> None:
        self.draw_cell(is_in_completed_garden=True)

    def set_neighbor_map(self, neighbor_cell_map: dict[Direction, Cell]) -> None:
        self.neighbor_cell_map = neighbor_cell_map

    def is_inside_cell(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def handle_cell_click(self) -> Optional[CellChangeInfo]:
        if not self.is_clickable:
            return

        new_cell_state = self.cell_state.get_next_in_cycle()
        return self.update_cell_state(new_cell_state)

    def update_cell_state(self, new_cell_state: CellState) -> Optional[CellChangeInfo]:
        old_cell_state = self.cell_state
        self.cell_state = new_cell_state
        self.draw_cell(is_in_completed_garden=False)
        return CellChangeInfo(before_state=old_cell_state, after_state=self.cell_state)

    def get_adjacent_neighbors(self) -> list[Cell]:
        return [self.get_neighbor(direction) for direction in ADJACENT_DIRECTIONS
                if direction in self.neighbor_cell_map.keys()]

    def get_neighbors(self, directions: Iterable[Direction]) -> list[Cell]:
        return [self.get_neighbor(direction) for direction in directions]

    def get_neighbor(self, direction: Direction) -> Cell:
        try:
            return self.neighbor_cell_map[direction]
        except KeyError:
            raise NonExistentNeighbor(f'{str(self)} has no neighbor in {direction}')

    def does_form_two_by_two_walls(self) -> bool:
        """Returns True if this cell is the top left corner of a two by two section of walls."""
        directions = (Direction.RIGHT, Direction.RIGHT_DOWN, Direction.DOWN)
        if self.cell_state.is_wall():
            try:
                neighbor_cells = self.get_neighbors(directions)
                return all(neighbor_cell.cell_state.is_wall() for neighbor_cell in neighbor_cells)
            except NonExistentNeighbor:
                # Can't be top-left of two by two since this is on the right or lower edge of board so the required
                # neighbors do not exist
                pass
        return False

    def __str__(self) -> str:
        return (f'Cell(row={self.row_number}, col={self.col_number}, state={self.cell_state}, '
                f'initial_value={self.initial_value})')
