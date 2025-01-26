from line_profiler import profile
from ...cell_change_info import CellChanges, CellStateChange
from ...cell_state import CellState
from ..board_state_checker import NoPossibleSolutionFromCurrentStateError
from ..rule_trigger import ALL_POSSIBLE_CELL_STATE_CHANGES
from .abstract_solver_rule import SolverRule


class NoIsolatedWallSectionsNaive(SolverRule):
    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return ALL_POSSIBLE_CELL_STATE_CHANGES

    @staticmethod
    def _get_rule_cost() -> float:
        return 36

    @staticmethod
    def _is_saturating_rule() -> bool:
        return False

    @profile
    def apply_rule(self) -> CellChanges:
        """
        All walls must be connected vertically or horizontally. If there is a wall that only has one "escape route" to
        connect to other walls, set that escape route cell to a wall. This is a cheap, but somewhat naive check since it
        only checks if a wall section has a single empty adjacent cell. This solver rule does not check if other
        non-adjacent cells are critical to allowing all the wall sections to connect. That check is done in
        NoIsolatedWallSections which is a more comprehensive check, but also more expensive.
        """
        cell_changes = CellChanges()
        wall_sections = self.board.get_all_wall_sections()
        if len(wall_sections) == 1:
            # If there is one wall section, then we don't know that the wall section needs to expand
            return cell_changes

        # TODO: can make this run multiple at once, but it still won't be saturating
        for wall_section in wall_sections:
            escape_routes = wall_section.get_empty_adjacent_neighbors()
            if len(escape_routes) == 0:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Isolated wall section',
                    problem_cell_groups=frozenset({wall_section}),
                )
            if len(escape_routes) == 1:
                only_escape_route = next(iter(escape_routes))  # Get first item in the list
                cell_changes.add_change(
                    self.set_cell_to_state(
                        only_escape_route, CellState.WALL, reason='Ensure no naively isolated wall sections'
                    )
                )
                # Because a cell was changed to a wall, the previously calculated wall_sections is no longer valid
                return cell_changes
        return cell_changes
