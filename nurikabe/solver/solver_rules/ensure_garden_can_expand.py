from .abstract_solver_rule import SolverRule
from ..board_state_checker import NoPossibleSolutionFromCurrentState
from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ...cell_group import CellGroup


class EnsureGardenCanExpand(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        If there is an incomplete garden and only one empty cell adjacent to the garden, the garden must expand via
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
                # Since some cells were marked as non-walls, the previously calculated all_gardens is no longer valid
                return cell_changes
        return cell_changes

    def handle_undersized_garden_escape_routes(self, non_wall_cell_group: CellGroup) -> CellChanges:
        cell_changes = CellChanges()
        escape_route_cells = non_wall_cell_group.get_empty_adjacent_neighbors()
        if len(escape_route_cells) == 1:
            only_escape_route_cell = list(escape_route_cells)[0]
            cell_changes.add_change(self.set_cell_to_state(only_escape_route_cell, CellState.NON_WALL,
                                                           reason='Ensure garden can expand'))
        return cell_changes
