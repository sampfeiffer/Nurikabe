from ...cell_change_info import CellChanges
from ...cell_group import CellGroup
from ...cell_state import CellState
from ..board_state_checker import NoPossibleSolutionFromCurrentStateError
from .abstract_solver_rule import SolverRule


class EnsureNoTwoByTwoWalls(SolverRule):
    CELL_COUNT_IN_TWO_BY_TWO_SECTION = 4

    def apply_rule(self) -> CellChanges:
        """
        If marking an empty cell as a wall would create a two-by-two section of walls, then that cell must be a
        non-wall. We define a cell as being the start of a two-by-two section of walls if it is the top-left cell in the
        group of walls. Because of this, we don't bother checking any cell in the bottom row or the right most column
        since it cannot be the start of a two-by-two group of walls.
        """
        cell_changes = CellChanges()
        for row in self.board.cell_grid[:-1]:
            for cell in row[:-1]:
                two_by_two_section = cell.get_two_by_two_section()
                two_by_two_section_num_of_walls = len([cell for cell in two_by_two_section
                                                       if cell.cell_state.is_wall()])
                if two_by_two_section_num_of_walls == self.CELL_COUNT_IN_TWO_BY_TWO_SECTION - 1:
                    for cell_corner in two_by_two_section:
                        if cell_corner.cell_state.is_empty():
                            cell_changes.add_change(self.set_cell_to_state(cell_corner, CellState.NON_WALL,
                                                                           reason='No two-by-two walls'))
                elif two_by_two_section_num_of_walls == self.CELL_COUNT_IN_TWO_BY_TWO_SECTION:
                    raise NoPossibleSolutionFromCurrentStateError(
                        message='There is a two-by-two section of walls',
                        problem_cell_groups=frozenset({CellGroup(two_by_two_section)}),
                    )
        return cell_changes
