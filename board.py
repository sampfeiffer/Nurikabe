from typing import Optional, Callable
import pygame

from screen import Screen
from level import Level
from cell import Cell
from pixel_position import PixelPosition
from color import Color
from cell_change_info import CellChangeInfo
from direction import Direction
from grid_coordinate import GridCoordinate
from garden import Garden
from wall_section import WallSection


class Board:
    def __init__(self, level: Level, screen: Screen):
        self.level = level
        self.screen = screen

        self.rect = self.get_board_rect()
        self.draw_board_rect()
        self.cell_grid = self.create_cell_grid()
        self.flat_cell_list = self.get_flat_cell_list()
        self.set_cell_neighbors()
        self.is_board_frozen = False

    def get_board_rect(self) -> pygame.Rect:
        top_left_of_board = self.screen.top_left_of_board
        width = self.screen.cell_width * self.level.number_of_columns
        height = self.screen.cell_width * self.level.number_of_rows
        return pygame.Rect(top_left_of_board.x_coordinate, top_left_of_board.y_coordinate, width, height)

    def draw_board_rect(self) -> None:
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)

    def create_cell_grid(self) -> list[list[Cell]]:
        return [[self.create_cell(row_number, col_number, cell_clue) for col_number, cell_clue in enumerate(row)]
                for row_number, row in enumerate(self.level.level_setup)]

    def create_cell(self, row_number: int, col_number: int, cell_clue: Optional[int]) -> Cell:
        cell_pixel_position = self.screen.get_cell_location(self.rect, row_number, col_number)
        return Cell(row_number, col_number, cell_clue, cell_pixel_position, self.screen)

    def get_flat_cell_list(self) -> list[Cell]:
        """Get a one dimensional list of cells. This is useful for easier looping."""
        return [cell for row in self.cell_grid for cell in row]

    def get_cell_from_grid(self, row_number: int, col_number: int) -> Cell:
        return self.cell_grid[row_number][col_number]

    def set_cell_neighbors(self) -> None:
        """
        For each cell, set a mapping of Direction->Cell. Cells on the edges/corners of the board will have fewer
        neighbors in this mapping.
        """
        for cell in self.flat_cell_list:
            neighbor_cell_map: dict[Direction, Cell] = {}
            for direction in Direction:
                neighbor_cell = self.get_neighbor_cell(cell, direction)
                if neighbor_cell is not None:
                    neighbor_cell_map[direction] = neighbor_cell
            cell.set_neighbor_map(neighbor_cell_map)

    def get_neighbor_cell(self, cell: Cell, direction: Direction) -> Optional[Cell]:
        neighbor_coordinate = cell.grid_coordinate.get_offset(direction)
        if self.is_valid_cell_coordinate(neighbor_coordinate):
            return self.get_cell_from_grid(row_number=neighbor_coordinate.row_number,
                                           col_number=neighbor_coordinate.col_number)

    def is_valid_cell_coordinate(self, grid_coordinate: GridCoordinate) -> bool:
        return 0 <= grid_coordinate.row_number < self.level.number_of_rows and \
            0 <= grid_coordinate.col_number < self.level.number_of_columns

    def handle_board_click(self, event_position: PixelPosition) -> Optional[CellChangeInfo]:
        if self.is_board_frozen:
            return
        if not self.is_inside_board(event_position):
            return
        for cell in self.flat_cell_list:
            if cell.is_inside_cell(event_position):
                cell_change_info = cell.handle_cell_click()
                self.update_painted_gardens()
                return cell_change_info

    def is_inside_board(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def update_painted_gardens(self) -> None:
        self.draw_all_cells()  # first redraw the board to "unpaint" gardens
        self.paint_completed_gardens()

    def draw_all_cells(self) -> None:
        for cell in self.flat_cell_list:
            cell.draw_cell()

    def paint_completed_gardens(self) -> None:
        gardens = self.get_all_gardens()
        for garden in gardens:
            garden.paint_garden_if_completed()

    def get_all_gardens(self) -> set[Garden]:
        gardens: set[Garden] = set()
        cells_in_gardens: set[Cell] = set()  # to prevent double counting
        for cell in self.flat_cell_list:
            if cell in cells_in_gardens or cell.cell_state.is_wall():
                continue
            garden = self.get_garden(starting_cell=cell)
            gardens.add(garden)
            cells_in_gardens = cells_in_gardens.union(garden.cells)
        return gardens

    def get_garden(self, starting_cell: Cell) -> Garden:
        cells = self.get_connected_cells(starting_cell, cell_criteria_func=lambda cell: not cell.cell_state.is_wall())
        return Garden(cells)

    def get_all_wall_sections(self) -> set[WallSection]:
        wall_sections: set[WallSection] = set()
        cells_in_wall_section: set[Cell] = set()  # to prevent double counting
        for cell in self.flat_cell_list:
            if cell in cells_in_wall_section or not cell.cell_state.is_wall():
                continue
            wall_section = self.get_wall_section(starting_cell=cell)
            wall_sections.add(wall_section)
            cells_in_wall_section = cells_in_wall_section.union(wall_section.cells)
        return wall_sections

    def get_wall_section(self, starting_cell: Cell) -> WallSection:
        cells = self.get_connected_cells(starting_cell, cell_criteria_func=lambda cell: cell.cell_state.is_wall())
        return WallSection(cells)

    def get_connected_cells(self, starting_cell: Cell, cell_criteria_func: Callable[[Cell], bool],
                            connected_cells: Optional[set[Cell]] = None) -> set[Cell]:
        """
        Get a list of cells that are connected (non-diagonally) to the starting cell where the cell_criteria_func
        returns True.
        """
        if connected_cells is None:
            connected_cells = set()
        if starting_cell in connected_cells:
            # Already visited this cell
            return connected_cells
        if cell_criteria_func(starting_cell):
            connected_cells.add(starting_cell)
            for neighbor_cell in starting_cell.get_adjacent_neighbors():
                self.get_connected_cells(neighbor_cell, cell_criteria_func, connected_cells)

        return connected_cells

    def freeze_cells(self) -> None:
        self.is_board_frozen = True
