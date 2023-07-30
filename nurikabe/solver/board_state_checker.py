from ..board import Board


class NoPossibleSolutionFromCurrentState(Exception):
    """
    This exception indicates that given the current state of the board, there is no possible solution. This means that
    cells that are marked as either clues, walls, or non-walls are breaking one or more of the rules of a solves
    Nurikabe puzzle.
    """
    pass


class BoardStateChecker:
    """Functionality to check if the board is in a state that is solvable."""
    def __init__(self, board: Board):
        self.board = board

    def check_for_board_state_issue(self) -> None:
        """Throw an error if the current state of the board is unsolvable"""
        self.check_for_two_by_two_section_of_walls()
        self.check_for_isolated_walls()
        self.check_for_garden_with_multiple_clues()
        self.check_for_too_small_garden()

    def check_for_two_by_two_section_of_walls(self) -> None:
        if self.board.has_two_by_two_wall():
            raise NoPossibleSolutionFromCurrentState('There is a two-by-two section of walls')

    def check_for_isolated_walls(self) -> None:
        wall_cells = self.board.get_wall_cells()
        if len(wall_cells) == 0:
            # Trivially, walls cannot be isolated if there are no wall cells
            return

        # Arbitrarily pick one wall cell, and ensure that if we flood adjacent cells while keeping garden cells off
        # limits, we can reach every other wall cell
        seed_wall_cell = list(wall_cells)[0]
        connected_non_garden_cells = self.board.get_connected_cells(
            starting_cell=seed_wall_cell,
            cell_criteria_func=lambda cell: not cell.cell_state.is_garden()
        )
        unreachable_wall_cells = wall_cells - connected_non_garden_cells
        if len(unreachable_wall_cells) > 0:
            raise NoPossibleSolutionFromCurrentState('Wall cells cannot connect')

    def check_for_garden_with_multiple_clues(self) -> None:
        gardens = self.board.get_all_gardens()
        for garden in gardens:
            if garden.get_number_of_clues() > 1:
                raise NoPossibleSolutionFromCurrentState('A garden cannot contain more than one clue')

    def check_for_too_small_garden(self) -> None:
        weak_gardens = self.board.get_all_weak_gardens()
        weak_gardens_with_one_clue = {weak_garden for weak_garden in weak_gardens
                                      if weak_garden.does_have_exactly_one_clue()}

        for weak_garden in weak_gardens_with_one_clue:
            if len(weak_garden.cells) < weak_garden.get_expected_garden_size():
                raise NoPossibleSolutionFromCurrentState('Garden is too small')
