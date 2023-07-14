import logging

from screen import Screen
from board import Board
from cell import Cell
from cell_state import CellState
from cell_group import CellGroup
from garden import Garden

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
        self.mark_naively_unreachable_cells_from_clue_cell_as_walls()
        self.mark_naively_unreachable_cells_from_garden_as_walls()
        self.separate_gardens_with_clues()
        self.fill_weak_garden_if_appropriate_size()

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
        for cell in self.board.get_empty_cells():
            if len([cell for adjacent_cell in cell.get_adjacent_neighbors() if adjacent_cell.has_clue]) > 1:
                self.set_cell_to_state(cell, CellState.WALL, reason='separate clues')

    def ensure_no_isolated_wall_sections(self) -> None:
        wall_sections = self.board.get_all_wall_sections()
        # TODO -  first ensure that there needs to be an "escape" for the wall section
        for wall_section in wall_sections:
            escape_routes = wall_section.get_empty_adjacent_neighbors()
            if len(escape_routes) == 1:
                only_escape_route = list(escape_routes)[0]
                self.set_cell_to_state(only_escape_route, CellState.WALL, reason='ensure no isolated wall sections')
                return  # wall_sections is no longer valid

    def ensure_garden_can_expand(self) -> None:
        """
        If there is an incomplete garden and only one empty cell adjacent to the garden, the garden must extend via
        that cell, so mark that cell as part of the garden.
        """
        all_gardens = self.board.get_all_gardens()
        for garden in all_gardens:
            number_of_clues = garden.get_number_of_clues()
            has_cell_state_changed = False
            if number_of_clues == 0:
                has_cell_state_changed = self.handle_undersized_garden_escape_routes(garden)
            elif number_of_clues == 1:
                clue = garden.get_clue_value()
                if len(garden.cells) < clue:
                    has_cell_state_changed = self.handle_undersized_garden_escape_routes(garden)
            else:
                raise NoPossibleSolutionFromCurrentState('Non-wall cell group contains more than one clue')
            if has_cell_state_changed:
                return  # all_gardens is no longer valid

    def handle_undersized_garden_escape_routes(self, non_wall_cell_group: CellGroup) -> bool:
        """Returns True is a cell state has been changed"""
        escape_routes = non_wall_cell_group.get_empty_adjacent_neighbors()
        if len(escape_routes) == 1:
            only_escape_route = list(escape_routes)[0]
            self.set_cell_to_state(only_escape_route, CellState.NON_WALL, reason='ensure garden can expand')
            return True
        else:
            return False

    def enclose_full_garden(self) -> None:
        """If there is a complete garden, enclose it with walls."""
        all_gardens = self.board.get_all_gardens()
        for garden in all_gardens:
            number_of_clues = garden.get_number_of_clues()
            if number_of_clues == 0:
                # This group of cells does not contain a clue. Therefore, it is not complete and should not be enclosed.
                pass
            elif number_of_clues == 1:
                clue = garden.get_clue_value()
                if len(garden.cells) == clue:
                    empty_adjacent_neighbors = garden.get_empty_adjacent_neighbors()
                    for cell in empty_adjacent_neighbors:
                        self.set_cell_to_state(cell, CellState.WALL, reason='enclose full garden')
            else:
                raise NoPossibleSolutionFromCurrentState('Garden contains more than one clue')

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
                        if cell_corner.cell_state.is_empty():
                            self.set_cell_to_state(cell_corner, CellState.NON_WALL, reason='no two-by-two walls')
                elif len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 4:
                    raise NoPossibleSolutionFromCurrentState('There is a two-by-two section of walls')

    def mark_naively_unreachable_cells_from_clue_cell_as_walls(self) -> None:
        """
        If there are any empty cells that are naively unreachable by a clue cell, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be allowed.
        This is a much cheaper check compared to proper path finding algorithms.
        """

        clue_cell_list = [cell for cell in self.board.flat_cell_list if cell.has_clue]
        for cell in self.board.get_empty_cells():
            is_cell_reachable_by_a_clue = False
            for clue_cell in clue_cell_list:
                # Here we do the clue value minus 1 since one garden spot is already taken by the clue cell itself
                if cell.get_manhattan_distance(clue_cell) <= clue_cell.clue - 1:
                    is_cell_reachable_by_a_clue = True
                    break
            if not is_cell_reachable_by_a_clue:
                self.set_cell_to_state(cell, CellState.WALL, reason='not Manhattan reachable by any clue cells')

    def mark_naively_unreachable_cells_from_garden_as_walls(self) -> None:
        """
        If there are any empty cells that are naively unreachable by a garden, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be
        allowed. This checks if cells are reachable from a garden in the remaining number of missing non-wall cells
        for that garden.
        """

        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        incomplete_gardens_and_remaining_sizes = [
            (incomplete_garden, incomplete_garden.get_num_of_remaining_garden_cells())
            for incomplete_garden in incomplete_gardens
        ]

        for cell in self.board.get_empty_cells():
            is_cell_reachable_by_a_clue = False
            for incomplete_garden, remaining_garden_size, in incomplete_gardens_and_remaining_sizes:
                if incomplete_garden.get_shortest_manhattan_distance_to_cell(cell) <= remaining_garden_size:
                    is_cell_reachable_by_a_clue = True
                    break
            if not is_cell_reachable_by_a_clue:
                self.set_cell_to_state(cell, CellState.WALL, reason='not Manhattan reachable by any gardens')

    def get_incomplete_gardens(self, with_clue_only: bool) -> set[Garden]:
        all_gardens = self.board.get_all_gardens()
        incomplete_gardens = {garden for garden in all_gardens if not garden.is_garden_correct_size()}
        if with_clue_only:
            incomplete_gardens = {garden for garden in incomplete_gardens if garden.does_contain_clue()}
        return incomplete_gardens

    def separate_gardens_with_clues(self) -> None:
        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        all_empty_adjacent_cells: set[Cell] = set()
        for incomplete_garden in incomplete_gardens:
            empty_adjacent_cells = incomplete_garden.get_empty_adjacent_neighbors()
            for cell in empty_adjacent_cells:
                if cell in all_empty_adjacent_cells:
                    self.set_cell_to_state(cell, CellState.WALL, reason='Adjacent to multiple gardens')
                all_empty_adjacent_cells.add(cell)

    def fill_weak_garden_if_appropriate_size(self) -> None:
        """
        If there is a weak garden that is the correct size but has some empty cells, mark the empty cells as non-walls.
        """
        all_weak_gardens = self.board.get_all_weak_gardens()
        for weak_garden in all_weak_gardens:
            if weak_garden.does_have_exactly_one_clue() and weak_garden.is_garden_correct_size():
                empty_cells = {cell for cell in weak_garden.cells if cell.cell_state.is_empty()}
                for cell in empty_cells:
                    self.set_cell_to_state(cell, CellState.NON_WALL, reason='Fill completed weak garden')


