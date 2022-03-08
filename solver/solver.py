import logging

from screen import Screen
from board import Board
from cell import Cell
from cell_state import CellState
from cell_group import CellGroup

logger = logging.getLogger(__name__)


class Solver:
    def __init__(self, screen: Screen, board: Board):
        self.screen = screen
        self.board = board

    def run_solver(self) -> None:
        self.separate_clues()
        self.ensure_no_isolated_wall_sections()
        self.ensure_garden_can_expand()
        self.enclose_full_garden()
        self.ensure_no_two_by_two_walls()

        self.board.update_painted_gardens()
        self.screen.update_screen()

    @staticmethod
    def set_cell_to_state(cell: Cell, target_cell_state: CellState, reason: str) -> None:
        if not cell.is_clickable:
            raise RuntimeError(f'cell is not clickable: {cell}')
        logger.debug(f'Setting {cell} to {target_cell_state}. Reason: {reason}')
        cell.update_cell_state(target_cell_state)

    def separate_clues(self) -> None:
        non_clue_cells = [cell for cell in self.board.flat_cell_list
                          if not cell.has_clue and cell.cell_state is CellState.EMPTY]
        for cell in non_clue_cells:
            if len([cell for adjacent_cell in cell.get_adjacent_neighbors() if adjacent_cell.has_clue]) > 1:
                self.set_cell_to_state(cell, CellState.WALL, reason='separate clues')

    def ensure_no_isolated_wall_sections(self) -> None:
        wall_sections = self.board.get_all_wall_sections()
        # TODO -  first ensure that there needs to be an "escape" for the wall section
        for wall_section in wall_sections:
            escape_routes = wall_section.get_empty_adjacent_neighbors()
            if len(escape_routes) == 1:
                only_escape_route = escape_routes[0]
                self.set_cell_to_state(only_escape_route, CellState.WALL, reason='ensure no isolated wall sections')
                return  # wall_sections is no longer valid

    def ensure_garden_can_expand(self) -> None:
        all_non_wall_cell_groups = self.get_all_non_wall_cell_groups()
        for non_wall_cell_group in all_non_wall_cell_groups:
            if non_wall_cell_group.does_contain_clue():
                clue = non_wall_cell_group.get_clue_value()
                if len(non_wall_cell_group.cells) < clue:
                    escape_routes = non_wall_cell_group.get_empty_adjacent_neighbors()
                    if len(escape_routes) == 1:
                        only_escape_route = escape_routes[0]
                        self.set_cell_to_state(only_escape_route, CellState.NON_WALL, reason='ensure garden can expand')

    def get_all_non_wall_cell_groups(self) -> set[CellGroup]:
        return self.board.get_all_cell_groups(cell_criteria_func=lambda cell: cell.is_non_wall_or_has_clue())

    def enclose_full_garden(self) -> None:
        all_non_wall_cell_groups = self.get_all_non_wall_cell_groups()
        for non_wall_cell_group in all_non_wall_cell_groups:
            if non_wall_cell_group.does_contain_clue():
                clue = non_wall_cell_group.get_clue_value()
                if len(non_wall_cell_group.cells) == clue:
                    empty_adjacent_neighbors = non_wall_cell_group.get_empty_adjacent_neighbors()
                    for cell in empty_adjacent_neighbors:
                        self.set_cell_to_state(cell, CellState.WALL, reason='enclose full garden')

    def ensure_no_two_by_two_walls(self) -> None:
        for row in self.board.cell_grid[:-1]:
            for cell in row[:-1]:
                two_by_two_section = cell.get_two_by_two_section()
                if len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 3:
                    for cell_corner in two_by_two_section:
                        if cell_corner.cell_state is CellState.EMPTY and not cell_corner.has_clue:
                            self.set_cell_to_state(cell_corner, CellState.NON_WALL, reason='no two-by-two walls')
