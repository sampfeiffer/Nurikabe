import logging

from screen import Screen
from board import Board
from cell import Cell
from cell_state import CellState
from cell_group import CellGroup

logger = logging.getLogger(__name__)


class NoPossibleSolutionFromCurrentState(Exception):
    """
    This exception indicates that given the current state of the board, there is no possible solution. This means that
    cells that are marked as either clues, walls, or non-walls are breaking one or more of the rules of a solves
    Nurikabe puzzle.
    """
    pass


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
        """
        A cell must be a wall if it is adjacent (non-diagonally) to more than one cell with a clue since gardens cannot
        have more than one clue.
        """
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
        """
        If there is an incomplete garden and only one empty cell adjacent to the garden, the garden must extend via
        that cell, so mark that cell as part of the garden.
        """
        all_non_wall_cell_groups = self.get_all_non_wall_cell_groups()
        for non_wall_cell_group in all_non_wall_cell_groups:
            number_of_clues = non_wall_cell_group.get_number_of_clues()
            if number_of_clues == 0:
                # We can't determine if the garden needs to expand
                pass
            elif number_of_clues == 1:
                clue = non_wall_cell_group.get_clue_value()
                if len(non_wall_cell_group.cells) < clue:
                    escape_routes = non_wall_cell_group.get_empty_adjacent_neighbors()
                    if len(escape_routes) == 1:
                        only_escape_route = escape_routes[0]
                        self.set_cell_to_state(only_escape_route, CellState.NON_WALL, reason='ensure garden can expand')
            else:
                raise NoPossibleSolutionFromCurrentState('Non-wall cell group contains more than one clue')

    def get_all_non_wall_cell_groups(self) -> set[CellGroup]:
        return self.board.get_all_cell_groups(cell_criteria_func=lambda cell: cell.is_non_wall_or_has_clue())

    def enclose_full_garden(self) -> None:
        """If there is a complete garden, enclose it with walls."""
        all_non_wall_cell_groups = self.get_all_non_wall_cell_groups()
        for non_wall_cell_group in all_non_wall_cell_groups:
            number_of_clues = non_wall_cell_group.get_number_of_clues()
            if number_of_clues == 0:
                # We can't determine if the garden is complete
                pass
            elif number_of_clues == 1:
                clue = non_wall_cell_group.get_clue_value()
                if len(non_wall_cell_group.cells) == clue:
                    empty_adjacent_neighbors = non_wall_cell_group.get_empty_adjacent_neighbors()
                    for cell in empty_adjacent_neighbors:
                        self.set_cell_to_state(cell, CellState.WALL, reason='enclose full garden')
            else:
                raise NoPossibleSolutionFromCurrentState('Non-wall cell group contains more than one clue')

    def ensure_no_two_by_two_walls(self) -> None:
        """
        If marking an empty cell as a wall would create a two-by-two section of walls, then it must be a non-wall.
        We define a cell as being the start of a two-by-two section of walls if it is the top-left cell in the group of
        walls. Because of this, don't bother checking any cell in the bottom row or the right most column since it
        cannot be the start of a two-by-two group of walls.
        """
        for row in self.board.cell_grid[:-1]:
            for cell in row[:-1]:
                two_by_two_section = cell.get_two_by_two_section()
                if len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 3:
                    for cell_corner in two_by_two_section:
                        if cell_corner.cell_state is CellState.EMPTY and not cell_corner.has_clue:
                            self.set_cell_to_state(cell_corner, CellState.NON_WALL, reason='no two-by-two walls')
                elif len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 4:
                    raise NoPossibleSolutionFromCurrentState('There is a two-by-two section of walls')
