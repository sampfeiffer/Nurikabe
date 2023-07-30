from .abstract_solver_rule import SolverRule
from ...cell_change_info import CellChanges
from ...cell_state import CellState


class NaivelyUnreachableFromClueCell(SolverRule):
    def apply_rule(self) -> CellChanges:
        """
        If there are any empty cells that are naively unreachable by a clue cell, it must be a wall. Here, naively means
        using the Manhattan distance between cells ignoring the fact that the path between the cells may not be allowed.
        This is a much cheaper check compared to proper path finding algorithms.
        """
        cell_changes = CellChanges()
        clue_cells = self.board.get_clue_cells()
        for cell in self.board.get_empty_cells():
            is_cell_reachable_by_a_clue = False
            for clue_cell in clue_cells:
                if cell.get_shortest_naive_path_length(clue_cell) <= clue_cell.clue:
                    is_cell_reachable_by_a_clue = True
                    break
            if not is_cell_reachable_by_a_clue:
                cell_changes.add_change(self.set_cell_to_state(cell, CellState.WALL,
                                                               reason='Not Manhattan reachable by any clue cells'))
        return cell_changes
