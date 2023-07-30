from .abstract_solver_rule import SolverRule
from ...cell_change_info import CellChanges
from ...cell_state import CellState


class NoIsolatedWallSections(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        All walls must be connected vertically or horizontally. If there is a wall that only has one "escape route" to
        connect to other walls, set that escape route cell to a wall.
        """
        cell_changes = CellChanges()
        wall_sections = self.board.get_all_wall_sections()
        if len(wall_sections) == 1:
            # If there is one wall section, then we don't know that the wall section needs to expand
            return cell_changes

        for wall_section in wall_sections:
            escape_routes = wall_section.get_empty_adjacent_neighbors()
            if len(escape_routes) == 1:
                only_escape_route = list(escape_routes)[0]
                cell_changes.add_change(self.set_cell_to_state(only_escape_route, CellState.WALL,
                                                               reason='Ensure no isolated wall sections'))
                # Because a cell was changed to a wall, the previously calculated wall_sections is no longer valid
                return cell_changes
        return cell_changes
