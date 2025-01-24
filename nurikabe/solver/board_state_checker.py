from ..board import Board
from ..cell_group import CellGroup


class NoPossibleSolutionFromCurrentStateError(Exception):
    """
    This exception indicates that given the current state of the board, there is no possible solution. This means that
    cells that are marked as either clues, walls, or non-walls are breaking one or more of the rules of a solved
    Nurikabe puzzle.
    """

    def __init__(self, message: str, problem_cell_groups: frozenset[CellGroup] | None = None):
        """Optionally can include information about which cell groups are causing the problem."""
        super().__init__(message)

        if problem_cell_groups is None:
            self.problem_cell_groups: frozenset[CellGroup] = frozenset()
        else:
            self.problem_cell_groups = problem_cell_groups


class BoardStateChecker:
    """Functionality to check if the board is in a state that is solvable."""

    def __init__(self, board: Board):
        self.board = board

    def check_for_board_state_issue(self) -> None:
        """Throw an error if the current state of the board is unsolvable."""
        self.check_for_two_by_two_section_of_walls()
        self.check_for_isolated_walls()
        self.check_for_garden_with_multiple_clues()
        self.check_for_too_small_garden()
        self.check_for_too_large_garden()
        self.check_for_enclosed_garden_with_no_clue()

    def check_for_two_by_two_section_of_walls(self) -> None:
        if self.board.has_two_by_two_wall():
            raise NoPossibleSolutionFromCurrentStateError(
                message='There is a two-by-two section of walls',
                problem_cell_groups=frozenset({CellGroup(self.board.get_two_by_two_wall_section_cells())}),
            )

    def check_for_isolated_walls(self, non_garden_cell_groups_with_walls: frozenset[CellGroup] | None = None) -> None:
        if non_garden_cell_groups_with_walls is None:
            non_garden_cell_groups_with_walls = self.board.get_all_non_garden_cell_groups_with_walls()
        if len(non_garden_cell_groups_with_walls) > 1:
            largest_non_garden_cell_group = max(
                non_garden_cell_groups_with_walls, key=lambda cell_group: len(cell_group.cells)
            )
            problem_cell_groups = non_garden_cell_groups_with_walls - {largest_non_garden_cell_group}
            problem_wall_groups = {
                CellGroup(cells={cell for cell in problem_cell_group.cells if cell.cell_state.is_wall()})
                for problem_cell_group in problem_cell_groups
            }
            raise NoPossibleSolutionFromCurrentStateError(
                message='Wall cells cannot connect',
                problem_cell_groups=frozenset(problem_wall_groups),
            )

    def check_for_garden_with_multiple_clues(self) -> None:
        gardens = self.board.get_all_gardens()
        for garden in gardens:
            if garden.get_number_of_clues() > 1:
                raise NoPossibleSolutionFromCurrentStateError(
                    message='A garden cannot contain more than one clue',
                    problem_cell_groups=frozenset({garden}),
                )

    def check_for_too_small_garden(self) -> None:
        weak_gardens = self.board.get_all_weak_gardens()
        weak_gardens_with_one_clue = {
            weak_garden for weak_garden in weak_gardens if weak_garden.does_have_exactly_one_clue()
        }

        for weak_garden in weak_gardens_with_one_clue:
            if len(weak_garden.cells) < weak_garden.get_expected_garden_size():
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Garden is too small',
                    problem_cell_groups=frozenset({weak_garden}),
                )

    def check_for_too_large_garden(self) -> None:
        gardens = self.board.get_all_gardens()
        gardens_with_one_clue = {garden for garden in gardens if garden.does_have_exactly_one_clue()}
        for garden in gardens_with_one_clue:
            if len(garden.cells) > garden.get_expected_garden_size():
                raise NoPossibleSolutionFromCurrentStateError(
                    message='Garden is too large',
                    problem_cell_groups=frozenset({garden}),
                )

    def check_for_enclosed_garden_with_no_clue(self) -> None:
        weak_gardens = self.board.get_all_weak_gardens()
        gardens_with_no_clue = {
            weak_garden
            for weak_garden in weak_gardens
            if not weak_garden.does_contain_clue() and weak_garden.has_non_wall_cell()
        }

        if len(gardens_with_no_clue) > 0:
            raise NoPossibleSolutionFromCurrentStateError(
                message='Garden has no clue',
                problem_cell_groups=frozenset(gardens_with_no_clue),
            )
