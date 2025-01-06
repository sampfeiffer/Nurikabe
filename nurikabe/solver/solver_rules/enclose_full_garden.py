from ...cell_change_info import CellChanges
from ...cell_state import CellState
from ..board_state_checker import NoPossibleSolutionFromCurrentStateError
from .abstract_solver_rule import SolverRule


class EncloseFullGarden(SolverRule):
    def apply_rule(self) -> CellChanges:
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
                        cell_changes.add_change(
                            self.set_cell_to_state(cell, CellState.WALL, reason='Enclose full garden')
                        )
            else:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Garden contains more than one clue',
                    problem_cell_groups=frozenset({garden}),
                )
        return cell_changes
