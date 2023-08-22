from __future__ import annotations
from typing import Optional, Iterable
import pygame

from .screen import Screen
from .cell_state import CellState
from .pixel_position import PixelPosition
from .color import Color
from .cell_change_info import CellChangeInfo
from .direction import Direction, ADJACENT_DIRECTIONS
from .grid_coordinate import GridCoordinate
from .rect_edge import RectEdge, get_rect_edges


class NonExistentNeighbor(Exception):
    pass


class Cell:
    CENTER_DOT = '\u2022'

    def __init__(self, row_number: int, col_number: int, clue: Optional[int], pixel_position: PixelPosition,
                 screen: Screen):
        self.row_number = row_number
        self.col_number = col_number
        self.grid_coordinate = GridCoordinate(row_number, col_number)
        self.clue = clue
        self.screen = screen

        self.has_clue = self.clue is not None
        self.is_clickable = not self.has_clue
        self.cell_state = CellState.CLUE if self.has_clue else CellState.EMPTY

        self.rect = self.get_rect(pixel_position)
        self.draw_cell()

        self.neighbor_cell_map: Optional[dict[Direction, Cell]] = None

    def get_rect(self, pixel_position: PixelPosition) -> pygame.Rect:
        width = self.screen.cell_width
        height = self.screen.cell_width
        return pygame.Rect(pixel_position.x_coordinate, pixel_position.y_coordinate, width, height)

    def draw_cell(self, is_in_completed_garden: bool = False, perimeter_color: Optional[Color] = None) -> None:
        if self.has_clue:
            self.draw_clue(is_in_completed_garden)
        elif self.cell_state.is_empty():
            self.draw_garden_cell()
        elif self.cell_state.is_wall():
            self.draw_wall_cell()
        elif self.cell_state.is_non_wall():
            self.draw_non_wall_cell(is_in_completed_garden)
        else:
            raise RuntimeError('This should not be possible')

        if perimeter_color is not None:
            self.draw_perimeter(perimeter_color)

    def draw_clue(self, is_in_completed_garden: bool) -> None:
        text = None if self.clue is None else str(self.clue)
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

    def draw_perimeter(self, perimeter_color: Color, should_update_screen_immediately: bool = False) -> None:
        self.screen.draw_rect(color=perimeter_color, rect=self.rect, width=3)
        if should_update_screen_immediately:
            self.screen.update_screen()

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

    def update_cell_state(self, new_cell_state: CellState) -> CellChangeInfo:
        old_cell_state = self.cell_state
        self.cell_state = new_cell_state
        self.draw_cell()
        return CellChangeInfo(grid_coordinate=self.grid_coordinate, before_state=old_cell_state,
                              after_state=self.cell_state)

    def get_adjacent_neighbors(self) -> set[Cell]:
        """Get a list of adjacent (non-diagonal) Cells."""
        return {self.get_neighbor(direction) for direction in ADJACENT_DIRECTIONS
                if direction in self.neighbor_cell_map.keys()}

    def get_neighbor_set(self, direction_list: Iterable[Direction]) -> set[Cell]:
        return {self.get_neighbor(direction) for direction in direction_list}

    def get_neighbor(self, direction: Direction) -> Cell:
        try:
            return self.neighbor_cell_map[direction]
        except KeyError:
            raise NonExistentNeighbor(f'{str(self)} has no neighbor in {direction}')

    def does_form_two_by_two_walls(self) -> bool:
        """Returns True if this cell is the top left corner of a two by two section of walls."""
        try:
            two_by_two_section = self.get_two_by_two_section()
            return all(cell.cell_state.is_wall() for cell in two_by_two_section)
        except NonExistentNeighbor:
            # Can't be top-left of two by two since this is on the right or lower edge of board so the required
            # neighbors do not exist
            return False

    def get_two_by_two_section(self) -> set[Cell]:
        """Return the two-by-two section of cells where this cell is the top-left corner."""
        direction_list = (Direction.RIGHT, Direction.RIGHT_DOWN, Direction.DOWN)
        neighbor_cells = self.get_neighbor_set(direction_list)
        return neighbor_cells.union({self})

    def has_any_clues_adjacent(self) -> bool:
        return any([neighbor_cell for neighbor_cell in self.get_adjacent_neighbors() if neighbor_cell.has_clue])

    def get_manhattan_distance(self, other_cell: Cell) -> int:
        """Get the Manhattan distance between this cell and the other cell."""
        return abs(self.row_number - other_cell.row_number) + abs(self.col_number - other_cell.col_number)

    def get_shortest_naive_path_length(self, other_cell: Cell) -> int:
        return self.get_manhattan_distance(other_cell) + 1

    def get_edges(self) -> set[RectEdge]:
        return get_rect_edges(self.rect)

    def __repr__(self) -> str:
        return (f'Cell(row={self.row_number}, col={self.col_number}, state={self.cell_state}, '
                f'clue={self.clue})')

    def as_simple_string(self) -> str:
        """Useful for printing the board with each cell state shown as a simple string"""
        if self.cell_state.is_clue():
            return str(self.clue)
        else:
            return {
                CellState.EMPTY: '_',
                CellState.WALL: 'X',
                CellState.NON_WALL: 'O',
            }[self.cell_state]
