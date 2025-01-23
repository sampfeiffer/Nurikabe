import pygame

from .cache.cache import Cache
from .cell import Cell
from .cell_change_info import CellChangeInfo, CellChanges
from .cell_group import CellGroup
from .cell_state import CellState, CellStateCriteriaFunc
from .color import Color
from .direction import Direction
from .garden import Garden
from .grid_coordinate import GridCoordinate
from .level import Level
from .pixel_position import PixelPosition
from .screen import Screen
from .wall_section import WallSection
from .weak_garden import WeakGarden


class AdjacentCluesError(Exception):
    pass


class Board:
    """Represents a board of cells."""

    def __init__(self, level: Level, screen: Screen):
        self.level = level
        self.screen = screen

        self.rect = self.get_board_rect()
        self.draw_board_rect()
        self.cell_grid = self.create_cell_grid()
        self.flat_cell_list = self.get_flat_cell_list()
        self.flat_cell_frozenset = frozenset(self.flat_cell_list)
        self.set_cell_neighbors()
        self.is_board_frozen = False

        self.ensure_no_adjacent_clues()

        self.cell_state_hash: int | None = None
        self.cache = Cache()

        self.clues_cells = self.get_clue_cells()

    def get_board_rect(self) -> pygame.Rect:
        top_left_of_board = self.screen.top_left_of_board
        width = self.screen.cell_width * self.level.number_of_columns
        height = self.screen.cell_width * self.level.number_of_rows
        return pygame.Rect(top_left_of_board.x_coordinate, top_left_of_board.y_coordinate, width, height)

    def draw_board_rect(self) -> None:
        self.screen.draw_rect(color=Color.OFF_WHITE, rect=self.rect, width=0)
        self.draw_outline()

    def draw_outline(self) -> None:
        rect = self.rect.copy()
        border_width = 2
        rect.topleft = (rect.left - border_width, rect.top - border_width)
        rect.width = rect.width + 2 * border_width
        rect.height = rect.height + 2 * border_width
        self.screen.draw_rect(color=Color.BLACK, rect=rect, width=border_width)

    def create_cell_grid(self) -> list[list[Cell]]:
        """Create a two-dimensional grid of cells."""
        return [
            [self.create_cell(row_number, col_number, cell_clue) for col_number, cell_clue in enumerate(row)]
            for row_number, row in enumerate(self.level.level_setup)
        ]

    def create_cell(self, row_number: int, col_number: int, cell_clue: int | None) -> Cell:
        cell_pixel_position = self.screen.get_cell_location(self.rect, row_number, col_number)
        return Cell(row_number, col_number, cell_clue, cell_pixel_position, self.screen)

    def get_flat_cell_list(self) -> list[Cell]:
        """Get a one dimensional list of cells. This is useful for easier looping."""
        return [cell for row in self.cell_grid for cell in row]

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

    def get_neighbor_cell(self, cell: Cell, direction: Direction) -> Cell | None:
        """
        Get the neighbor cell in the given direction.

        Returns None if there is no cell in that direction. E.g. If this cell is the top row and we are trying to
        extract the neighbor Direction.UP neighbor cell.
        """
        neighbor_coordinate = cell.grid_coordinate.get_offset(direction)
        if self.is_valid_cell_coordinate(neighbor_coordinate):
            neighbor_cell = self.get_cell_from_grid(
                row_number=neighbor_coordinate.row_number, col_number=neighbor_coordinate.col_number
            )
        else:
            neighbor_cell = None
        return neighbor_cell

    def is_valid_cell_coordinate(self, grid_coordinate: GridCoordinate) -> bool:
        return (
            0 <= grid_coordinate.row_number < self.level.number_of_rows
            and 0 <= grid_coordinate.col_number < self.level.number_of_columns
        )

    def get_cell_from_grid(self, row_number: int, col_number: int) -> Cell:
        return self.cell_grid[row_number][col_number]

    def ensure_no_adjacent_clues(self) -> None:
        """
        As a sanity check, ensure that there are no adjacent clue cells since that would break the rules of Nurikabe
        and be impossible to solve.
        """
        for cell in self.flat_cell_list:
            if cell.has_clue and cell.has_any_clues_adjacent():
                msg = 'This board setup is infeasible since there are adjacent clues'
                raise AdjacentCluesError(msg)

    def process_potential_left_click_down(self, event_position: PixelPosition) -> CellChangeInfo | None:
        if self.is_board_frozen:
            return None
        if not self.is_inside_board(event_position):
            return None

        # The click must be inside the board. Figure out which cell was clicked and process it appropriately
        for cell in self.flat_cell_list:
            if cell.is_inside_cell(event_position):
                cell_change_info = cell.handle_cell_click()
                self.reset_cell_state_hash()
                self.update_painted_gardens()
                return cell_change_info

        msg = 'Code should not be reachable'
        raise RuntimeError(msg)

    def is_inside_board(self, event_position: PixelPosition) -> bool:
        return self.rect.collidepoint(event_position.coordinates)

    def update_painted_gardens(self) -> None:
        # First redraw the board to "unpaint" gardens
        self.draw_outline()
        self.draw_all_cells()

        self.paint_completed_gardens()

    def draw_all_cells(self) -> None:
        for cell in self.flat_cell_list:
            cell.draw_cell()

    def paint_completed_gardens(self) -> None:
        """Grays out completed gardens to indicate to the user that they are complete."""
        for garden in self.get_all_gardens():
            garden.paint_garden_if_completed()

    def get_all_gardens(self) -> frozenset[Garden]:
        garden_cells = self.get_garden_cells()
        all_cell_groups = self.get_all_cell_groups_with_cache(valid_cells=garden_cells)
        return frozenset({Garden(cell_group.cells) for cell_group in all_cell_groups})

    def get_all_weak_gardens(self) -> frozenset[WeakGarden]:
        weak_garden_cells = self.get_weak_garden_cells()
        all_cell_groups = self.get_all_cell_groups_with_cache(valid_cells=weak_garden_cells)
        return frozenset({WeakGarden(cell_group.cells) for cell_group in all_cell_groups})

    def get_all_wall_sections(self) -> frozenset[WallSection]:
        wall_cells = self.get_wall_cells()
        all_cell_groups = self.get_all_cell_groups_with_cache(valid_cells=wall_cells)
        return frozenset({WallSection(cell_group.cells) for cell_group in all_cell_groups})

    def get_all_cell_groups_with_cache(self, valid_cells: frozenset[Cell]) -> frozenset[CellGroup]:
        """Calls get_all_cell_groups but leverages caching to speed up the code."""
        valid_cells_hash = hash(valid_cells)
        cell_state_hash = self.get_cell_state_hash()
        all_cell_groups_from_cache = self.cache.cell_groups_cache.extract_from_cache(
            cell_state_hash=cell_state_hash,
            valid_cells_hash=valid_cells_hash,
        )
        if all_cell_groups_from_cache is not None:
            return all_cell_groups_from_cache

        all_cell_groups = self.get_all_cell_groups(valid_cells)
        self.cache.cell_groups_cache.add_to_cache(
            cell_state_hash=cell_state_hash, valid_cells_hash=valid_cells_hash, all_cell_groups=all_cell_groups
        )
        return frozenset(all_cell_groups)

    def get_all_cell_groups(self, valid_cells: frozenset[Cell]) -> frozenset[CellGroup]:
        """
        Gets a frozenset of all CellGroups as defined by the flood fill of valid cells.

        For example, say valid_cells is a set of all wall cells. This function will the set of CellGroups where each
        CellGroup is a connected section of wall cells.

        Note that, as usual, the flood fill goes vertically and horizontally, but not diagonally.
        """
        all_cell_groups: set[CellGroup] = set()
        cells_already_in_a_group: set[Cell] = set()  # to prevent double counting
        for cell in valid_cells:
            if cell in cells_already_in_a_group:
                continue
            cell_group = self.get_cell_group(starting_cell=cell, valid_cells=valid_cells)
            all_cell_groups.add(cell_group)
            cells_already_in_a_group = cells_already_in_a_group.union(cell_group.cells)
        return frozenset(all_cell_groups)

    def get_garden(self, starting_cell: Cell) -> Garden:
        garden_cells = self.get_garden_cells()
        cells = self.get_connected_cells_with_cache(starting_cell, valid_cells=garden_cells)
        return Garden(cells)

    def get_wall_section(self, starting_cell: Cell) -> WallSection:
        wall_cells = self.get_wall_cells()
        cells = self.get_connected_cells_with_cache(starting_cell, valid_cells=wall_cells)
        return WallSection(cells)

    def get_cell_group(self, starting_cell: Cell, valid_cells: frozenset[Cell]) -> CellGroup:
        cells = self.get_connected_cells_with_cache(starting_cell, valid_cells)
        return CellGroup(cells)

    def get_connected_cells_with_cache(self, starting_cell: Cell, valid_cells: frozenset[Cell]) -> frozenset[Cell]:
        """Calls get_connected_cells but leverages caching to speed up the code."""
        cell_state_hash = self.get_cell_state_hash()
        valid_cells_hash = hash(valid_cells)
        connected_cells_from_cache = self.cache.connected_cells_cache.extract_from_cache(
            cell_state_hash=cell_state_hash,
            valid_cells_hash=valid_cells_hash,
            starting_cell=starting_cell,
        )
        if connected_cells_from_cache is not None:
            return connected_cells_from_cache

        connected_cells = frozenset(self.get_connected_cells(starting_cell, valid_cells))
        self.cache.connected_cells_cache.add_to_cache(
            cell_state_hash=cell_state_hash,
            valid_cells_hash=valid_cells_hash,
            starting_cell=starting_cell,
            connected_cells=frozenset(connected_cells),
        )
        return connected_cells

    def get_connected_cells(
        self, starting_cell: Cell, valid_cells: frozenset[Cell], connected_cells: set[Cell] | None = None
    ) -> set[Cell]:
        """
        Get a set of cells that are connected (non-diagonally) to the starting cell where the cell is in valid_cells.
        Basically this is a flood fill.
        """
        if connected_cells is None:
            connected_cells = set()
        connected_cells.add(starting_cell)

        additional_cells_to_check = starting_cell.get_adjacent_neighbors().intersection(valid_cells) - connected_cells
        for neighbor_cell in additional_cells_to_check:
            self.get_connected_cells(neighbor_cell, valid_cells, connected_cells)

        return connected_cells

    def freeze_cells(self) -> None:
        self.is_board_frozen = True

    def filter_cells(self, cell_state_criteria_func: CellStateCriteriaFunc) -> frozenset[Cell]:
        """Returns a frozenset of Cells whose state meets the cell_state_criteria_func. Leverages caching."""
        cell_state_hash = self.get_cell_state_hash()
        cell_set_from_cache = self.cache.cell_set_cache.extract_from_cache(cell_state_hash, cell_state_criteria_func)
        if cell_set_from_cache is not None:
            return cell_set_from_cache

        cell_set = frozenset({cell for cell in self.flat_cell_frozenset if cell_state_criteria_func(cell.cell_state)})
        self.cache.cell_set_cache.add_to_cache(cell_state_hash, cell_state_criteria_func, cells=cell_set)
        return cell_set

    def get_empty_cells(self) -> frozenset[Cell]:
        return self.filter_cells(CellState.is_empty_static)

    def get_wall_cells(self) -> frozenset[Cell]:
        return self.filter_cells(CellState.is_wall_static)

    def get_clue_cells(self) -> frozenset[Cell]:
        return self.filter_cells(CellState.is_clue_static)

    def get_garden_cells(self) -> frozenset[Cell]:
        return self.filter_cells(CellState.is_garden_static)

    def get_weak_garden_cells(self) -> frozenset[Cell]:
        return self.filter_cells(CellState.is_weak_garden_static)

    def apply_cell_changes(self, cell_changes: CellChanges) -> None:
        for cell_change_info in cell_changes.cell_change_list:
            cell = self.get_cell_from_grid(
                row_number=cell_change_info.grid_coordinate.row_number,
                col_number=cell_change_info.grid_coordinate.col_number,
            )
            cell.update_cell_state(new_cell_state=cell_change_info.after_state)
        self.reset_cell_state_hash()

    def has_two_by_two_wall(self) -> bool:
        return any(cell.does_form_two_by_two_walls() for cell in self.flat_cell_list)

    def get_two_by_two_wall_sections(self) -> frozenset[Cell]:
        two_by_two_wall_section_cells: set[Cell] = set()
        for cell in self.flat_cell_list:
            if cell.does_form_two_by_two_walls():
                two_by_two_wall_section_cells.update(cell.get_two_by_two_section())
        return frozenset(two_by_two_wall_section_cells)

    def get_all_non_garden_cell_groups_with_walls(
        self, additional_off_limit_cell: Cell | None = None
    ) -> frozenset[CellGroup]:
        off_limit_cells = set(self.get_garden_cells())
        if additional_off_limit_cell is not None:
            off_limit_cells.add(additional_off_limit_cell)

        valid_cells = frozenset(self.flat_cell_frozenset - off_limit_cells)
        non_garden_cell_groups = self.get_all_cell_groups_with_cache(valid_cells)
        return frozenset(
            {
                non_garden_cell_group
                for non_garden_cell_group in non_garden_cell_groups
                if non_garden_cell_group.does_contain_wall()
            }
        )

    def as_simple_string_list(self) -> list[str]:
        """
        Useful for printing the board with each cell state shown as a simple string.

        For example:
        [
            '_,_,W,2',
            'W,1,_,O',
            '_,_,_,W'
        ]
        """
        return [','.join([cell.as_simple_string() for cell in row]) for row in self.cell_grid]

    def reset_cell_state_hash(self) -> None:
        self.cell_state_hash = None

    def get_cell_state_hash(self) -> int:
        """Get a hash representation of the state of the cells in the board."""
        if self.cell_state_hash is None:
            self.cell_state_hash = hash(tuple(cell.cell_state.value for cell in self.flat_cell_list))
        return self.cell_state_hash
