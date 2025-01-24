from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ..board_state_checker import BoardStateChecker
from .abstract_solver_rule import SolverRule


class NoIsolatedWallSections(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        All walls must be connected vertically or horizontally. If there is an empty cell that would block all wall
        sections from connecting if it were to be marked as a non-wall, then it must be a wall cell. This solver rule is
        more expensive, but also more comprehensive than NoIsolatedWallSectionsNaive.
        """
        cell_changes = CellChanges()
        if len(self.board.get_wall_cells()) <= 1:
            return cell_changes

        BoardStateChecker(self.board).check_for_isolated_walls()

        for cell in self.board.get_empty_cells():
            cell_groups = self.board.get_all_non_garden_cell_groups_with_walls(additional_off_limit_cell=cell)
            if len(cell_groups) > 1:
                cell_changes.add_change(
                    self.set_cell_to_state(
                        cell,
                        CellState.WALL,
                        reason='Ensure no isolated wall sections',
                    ),
                )

        return cell_changes
