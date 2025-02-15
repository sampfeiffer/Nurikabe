from line_profiler import profile
from ...cell import Cell
from ...cell_change_info import CellChanges, CellStateChange
from ...cell_group import CellGroup
from ...cell_state import CellState
from ..board_state_checker import NoPossibleSolutionFromCurrentStateError
from ..rule_trigger import ALL_POSSIBLE_CELL_STATE_CHANGES
from .abstract_solver_rule import SolverRule


class EnsureGardenCanExpandOneRoute(SolverRule):
    # TODO: this is definitely covered by the combo of EnsureGardenWithClueCanExpand and
    #  EnsureGardenWithoutClueCanExpand. Should we keep this solver rule since it's cheap? Or should we remove since
    #  it's a duplicated check? This decision is pending some speed checks to see how much quicker this runs than the
    #  more complicated solver rules mentioned above.

    @staticmethod
    def _get_rule_triggers() -> frozenset[CellStateChange]:
        return ALL_POSSIBLE_CELL_STATE_CHANGES

    @staticmethod
    def _get_rule_cost() -> float:
        return 18

    @staticmethod
    def _is_saturating_rule() -> bool:
        return False

    @profile
    def apply_rule(self) -> CellChanges:
        """
        If there is an incomplete garden and only one empty cell adjacent to the garden, the garden must expand via
        that cell, so mark that cell as part of the garden.
        """
        cell_changes = CellChanges()
        all_gardens = self.board.get_all_gardens()
        all_escape_route_cells: set[Cell] = set()
        for garden in all_gardens:
            number_of_clues = garden.get_number_of_clues()
            if number_of_clues == 0:
                escape_route_cell = self.get_escape_route_cell(garden)
                if escape_route_cell:
                    all_escape_route_cells.add(escape_route_cell)
                # cell_changes.add_changes(self.handle_undersized_garden_escape_routes(garden))
            elif number_of_clues == 1:
                clue = garden.get_clue_value()
                if len(garden.cells) < clue:
                    # cell_changes.add_changes(self.handle_undersized_garden_escape_routes(garden))
                    escape_route_cell = self.get_escape_route_cell(garden)
                    if escape_route_cell:
                        all_escape_route_cells.add(escape_route_cell)
            else:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Garden contains more than one clue',
                    problem_cell_groups=frozenset({garden}),
                )
            # if cell_changes.has_any_changes():
            #     # Since some cells were marked as non-walls, the previously calculated all_gardens is no longer valid
            #     return cell_changes

        for escape_route_cell in all_escape_route_cells:
            cell_changes.add_change(
                self.set_cell_to_state(escape_route_cell, CellState.NON_WALL, reason='Ensure garden can expand')
            )
        return cell_changes

    @staticmethod
    def get_escape_route_cell(non_wall_cell_group: CellGroup) -> Cell | None:
        escape_route_cells = non_wall_cell_group.get_empty_adjacent_neighbors()
        if len(escape_route_cells) == 1:
            return next(iter(escape_route_cells))
        return None

    def handle_undersized_garden_escape_routes(self, non_wall_cell_group: CellGroup) -> CellChanges:
        cell_changes = CellChanges()
        escape_route_cells = non_wall_cell_group.get_empty_adjacent_neighbors()
        if len(escape_route_cells) == 1:
            only_escape_route_cell = next(iter(escape_route_cells))
            cell_changes.add_change(
                self.set_cell_to_state(only_escape_route_cell, CellState.NON_WALL, reason='Ensure garden can expand')
            )
        return cell_changes
