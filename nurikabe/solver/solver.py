import logging

from screen import Screen
from board import Board
from cell import Cell
from cell_state import CellState
from cell_group import CellGroup
from garden import Garden
from color import Color
from cell_change_info import CellChangeInfo, CellChanges
from undo_redo_control import UndoRedoControl

logger = logging.getLogger(__name__)


class NoPossibleSolutionFromCurrentState(Exception):
    """
    This exception indicates that given the current state of the board, there is no possible solution. This means that
    cells that are marked as either clues, walls, or non-walls are breaking one or more of the rules of a solves
    Nurikabe puzzle.
    """
    pass


class Solver:
    def __init__(self, screen: Screen, board: Board, undo_redo_control: UndoRedoControl):
        self.screen = screen
        self.board = board
        self.undo_redo_control = undo_redo_control

    def run_solver(self) -> CellChanges:
        cell_changes = CellChanges()

        cell_changes.add_changes(self.separate_clues())
        cell_changes.add_changes(self.ensure_no_isolated_wall_sections())
        cell_changes.add_changes(self.ensure_garden_can_expand())
        cell_changes.add_changes(self.enclose_full_garden())
        cell_changes.add_changes(self.ensure_no_two_by_two_walls())
        cell_changes.add_changes(self.mark_naively_unreachable_cells_from_clue_cell_as_walls())
        cell_changes.add_changes(self.mark_naively_unreachable_cells_from_garden_as_walls())
        cell_changes.add_changes(self.separate_gardens_with_clues())
        cell_changes.add_changes(self.fill_weak_garden_if_appropriate_size())
        cell_changes.add_changes(self.mark_unreachable_cells_from_garden_as_walls())

        self.board.update_painted_gardens()
        self.undo_redo_control.process_board_event(cell_changes)
        return cell_changes

    @staticmethod
    def set_cell_to_state(cell: Cell, target_cell_state: CellState, reason: str) -> CellChangeInfo:
        if not cell.is_clickable:
            raise RuntimeError(f'cell is not clickable: {cell}')
        logger.debug(f'Setting {cell} to {target_cell_state}. Reason: {reason}')
        return cell.update_cell_state(target_cell_state)

    def separate_clues(self) -> CellChanges:
        """
        A cell must be a wall if it is adjacent (non-diagonally) to more than one cell with a clue since gardens cannot
        have more than one clue.
        """
        cell_changes = CellChanges()
        for cell in self.board.get_empty_cells():
            if len([cell for adjacent_cell in cell.get_adjacent_neighbors() if adjacent_cell.has_clue]) > 1:
                cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL, reason='separate clues'))
        return cell_changes

    def ensure_no_isolated_wall_sections(self) -> CellChanges:
        cell_changes = CellChanges()
        wall_sections = self.board.get_all_wall_sections()
        # TODO -  first ensure that there needs to be an "escape" for the wall section
        for wall_section in wall_sections:
            escape_routes = wall_section.get_empty_adjacent_neighbors()
            if len(escape_routes) == 1:
                only_escape_route = list(escape_routes)[0]
                cell_changes.add_change(self.set_cell_to_state(only_escape_route, CellState.WALL,
                                                               reason='Ensure no isolated wall sections'))
                return cell_changes  # wall_sections is no longer valid
        return cell_changes

    def ensure_garden_can_expand(self) -> CellChanges:
        """
        If there is an incomplete garden and only one empty cell adjacent to the garden, the garden must extend via
        that cell, so mark that cell as part of the garden.
        """
        cell_changes = CellChanges()
        all_gardens = self.board.get_all_gardens()
        for garden in all_gardens:
            number_of_clues = garden.get_number_of_clues()
            if number_of_clues == 0:
                cell_changes.add_changes(self.handle_undersized_garden_escape_routes(garden))
            elif number_of_clues == 1:
                clue = garden.get_clue_value()
                if len(garden.cells) < clue:
                    cell_changes.add_changes(self.handle_undersized_garden_escape_routes(garden))
            else:
                raise NoPossibleSolutionFromCurrentState('Non-wall cell group contains more than one clue')
            if cell_changes.has_any_changes():
                return cell_changes  # all_gardens is no longer valid
        return cell_changes

    def handle_undersized_garden_escape_routes(self, non_wall_cell_group: CellGroup) -> CellChanges:
        cell_changes = CellChanges()
        escape_routes = non_wall_cell_group.get_empty_adjacent_neighbors()
        if len(escape_routes) == 1:
            only_escape_route = list(escape_routes)[0]
            cell_changes.add_change(self.set_cell_to_state(only_escape_route, CellState.NON_WALL,
                                                           reason='Ensure garden can expand'))
        return cell_changes

    def enclose_full_garden(self) -> CellChanges:
        """If there is a complete garden, enclose it with walls."""
        cell_changes = CellChanges()
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
                        cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                                       reason='Enclose full garden'))
            else:
                raise NoPossibleSolutionFromCurrentState('Garden contains more than one clue')
        return cell_changes

    def ensure_no_two_by_two_walls(self) -> CellChanges:
        """
        If marking an empty cell as a wall would create a two-by-two section of walls, then it must be a non-wall.
        We define a cell as being the start of a two-by-two section of walls if it is the top-left cell in the group of
        walls. Because of this, don't bother checking any cell in the bottom row or the right most column since it
        cannot be the start of a two-by-two group of walls.
        """
        cell_changes = CellChanges()
        for row in self.board.cell_grid[:-1]:
            for cell in row[:-1]:
                two_by_two_section = cell.get_two_by_two_section()
                if len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 3:
                    for cell_corner in two_by_two_section:
                        if cell_corner.cell_state.is_empty():
                            cell_changes.add_change(self.set_cell_to_state(cell_corner, CellState.NON_WALL,
                                                                           reason='No two-by-two walls'))
                elif len([cell for cell in two_by_two_section if cell.cell_state.is_wall()]) == 4:
                    raise NoPossibleSolutionFromCurrentState('There is a two-by-two section of walls')
        return cell_changes

    def mark_naively_unreachable_cells_from_clue_cell_as_walls(self) -> CellChanges:
        """
        If there are any empty cells that are naively unreachable by a clue cell, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be allowed.
        This is a much cheaper check compared to proper path finding algorithms.
        """
        cell_changes = CellChanges()
        clue_cell_list = [cell for cell in self.board.flat_cell_list if cell.has_clue]
        for cell in self.board.get_empty_cells():
            is_cell_reachable_by_a_clue = False
            for clue_cell in clue_cell_list:
                # Here we do the clue value minus 1 since one garden spot is already taken by the clue cell itself
                if cell.get_manhattan_distance(clue_cell) <= clue_cell.clue - 1:
                    is_cell_reachable_by_a_clue = True
                    break
            if not is_cell_reachable_by_a_clue:
                cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                               reason='Not Manhattan reachable by any clue cells'))
        return cell_changes

    def mark_naively_unreachable_cells_from_garden_as_walls(self) -> CellChanges:
        """
        If there are any empty cells that are naively unreachable by a garden, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be
        allowed. This checks if cells are reachable from a garden in the remaining number of missing non-wall cells
        for that garden.
        """
        cell_changes = CellChanges()
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
                cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                               reason='Not Manhattan reachable by any gardens'))
        return cell_changes

    def get_incomplete_gardens(self, with_clue_only: bool) -> set[Garden]:
        all_gardens = self.board.get_all_gardens()
        incomplete_gardens = {garden for garden in all_gardens if not garden.is_garden_correct_size()}
        if with_clue_only:
            incomplete_gardens = {garden for garden in incomplete_gardens if garden.does_contain_clue()}
        return incomplete_gardens

    def separate_gardens_with_clues(self) -> CellChanges:
        cell_changes = CellChanges()
        incomplete_gardens = self.get_incomplete_gardens(with_clue_only=True)
        all_empty_adjacent_cells: set[Cell] = set()
        for incomplete_garden in incomplete_gardens:
            empty_adjacent_cells = incomplete_garden.get_empty_adjacent_neighbors()
            for cell in empty_adjacent_cells:
                if cell in all_empty_adjacent_cells:
                    cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                                   reason='Adjacent to multiple gardens'))
                all_empty_adjacent_cells.add(cell)
        return cell_changes

    def fill_weak_garden_if_appropriate_size(self) -> CellChanges:
        """
        If there is a weak garden that is the correct size but has some empty cells, mark the empty cells as non-walls.
        """
        cell_changes = CellChanges()
        all_weak_gardens = self.board.get_all_weak_gardens()
        for weak_garden in all_weak_gardens:
            if weak_garden.does_have_exactly_one_clue() and weak_garden.is_garden_correct_size():
                empty_cells = {cell for cell in weak_garden.cells if cell.cell_state.is_empty()}
                for cell in empty_cells:
                    cell_changes.add_change(self.set_cell_to_state(cell, CellState.NON_WALL,
                                                                   reason='Fill completed weak garden'))
        return cell_changes

    def mark_unreachable_cells_from_garden_as_walls(self) -> CellChanges:
        """
        If there are any empty cells that are unreachable by a garden, it must be a wall. For any incomplete garden
        with a clue, this detects the reachable cells. If there are empty cells that are not reachable by all gardens
        with clues, then those empty cells must be walls.
        """

        cell_changes = CellChanges()
        gardens_with_clue = self.get_all_gardens_with_clue()
        incomplete_gardens_with_clue = {garden for garden in gardens_with_clue if not garden.is_garden_correct_size()}
        all_reachable_cells: set[Cell] = set()
        for incomplete_garden_with_clue in incomplete_gardens_with_clue:
            other_gardens_with_clues = gardens_with_clue - {incomplete_garden_with_clue}
            reachable_from_garden = self.get_cells_reachable_from_garden(incomplete_garden_with_clue,
                                                                         other_gardens_with_clues)
            all_reachable_cells = all_reachable_cells.union(reachable_from_garden)
        for cell in self.board.get_empty_cells():
            if cell not in all_reachable_cells:
                cell_changes.add_change(
                    self.set_cell_to_state(cell, CellState.WALL,
                                           reason='Not reachable by any incomplete gardens with clues')
                )
        return cell_changes

    def get_cells_reachable_from_garden(self, source_garden: Garden,
                                        other_gardens_with_clues: set[Garden]) -> set[Cell]:
        if not source_garden.does_have_exactly_one_clue():
            raise RuntimeError('Cannot determine reach of garden since there is not exactly one clue')
        num_of_remaining_garden_cells = source_garden.get_num_of_remaining_garden_cells()

        # Determine which cells are not able to be a part of the source_garden
        off_limits_cells = self.board.get_wall_cells()
        for garden in other_gardens_with_clues:
            off_limits_cells = off_limits_cells.union(garden.cells)
            off_limits_cells = off_limits_cells.union(garden.get_adjacent_neighbors())

        # Get the cells that can be accessed from source_garden without going through a cell in off_limits_cells
        reachable_cells = self.board.get_connected_cells(
            starting_cell=source_garden.get_clue_cell(),
            cell_criteria_func=lambda x: x not in off_limits_cells
        )

        # Remove cells that are not Manhattan reachable from the source_garden given the number of remaining garden
        # left in this incomplete source_garden
        reachable_cells = {
            cell for cell in reachable_cells
            if source_garden.get_shortest_manhattan_distance_to_cell(cell) <= num_of_remaining_garden_cells
        }

        return reachable_cells

    def get_cells_reachable_from_clue_cell(self, clue_cell: Cell) -> set[Cell]:
        if not clue_cell.has_clue:
            raise
        gardens_with_clues = self.get_all_gardens_with_clue()
        other_gardens_with_clues = {garden for garden in gardens_with_clues if clue_cell not in garden.cells}
        off_limits_cells = self.board.get_wall_cells()
        for garden in other_gardens_with_clues:
            off_limits_cells = off_limits_cells.union(garden.cells)
            off_limits_cells = off_limits_cells.union(garden.get_adjacent_neighbors())
        reachable_cells = self.board.get_connected_cells(
            clue_cell,
            cell_criteria_func=lambda x: x not in off_limits_cells
        )
        reachable_cells = {cell for cell in reachable_cells
                           if clue_cell.get_shortest_naive_path_length(cell) <= clue_cell.clue}
        return reachable_cells

    def get_all_gardens_with_clue(self) -> set[Garden]:
        all_gardens = self.board.get_all_gardens()
        return {garden for garden in all_gardens if garden.does_contain_clue()}

    def color_group(self, cells: set[Cell]) -> None:
        for cell in cells:
            cell.draw_perimeter(Color.YELLOW)
        self.screen.update_screen()
