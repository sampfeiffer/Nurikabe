from unittest import TestCase
from unittest.mock import MagicMock

from nurikabe.solver.board_state_checker import BoardStateChecker, NoPossibleSolutionFromCurrentStateError
from tests.build_board import build_board


class TestBoardStateChecker(TestCase):
    screen = MagicMock(name='Screen')

    def create_board_state_checker(self, board_details: list[str]) -> BoardStateChecker:
        board = build_board(self.screen, board_details)
        return BoardStateChecker(board)


class TestCheckForTwoByTwoSectionOfWalls(TestBoardStateChecker):
    def test_no_two_by_two_section_of_walls(self) -> None:
        """
        Ensure that when there are no two-by-two sections of walls, NoPossibleSolutionFromCurrentStateError is not
        raised.
        """
        board_details = [
            '1,_,_,W',
            'W,_,W,_',
            '_,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_two_by_two_section_of_walls()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_two_by_two_section_of_walls() raised NoPossibleSolutionFromCurrentStateError '
                      'unexpectedly')

    def test_has_two_by_two_section_of_walls(self) -> None:
        """
        Check that when a there is a two-by-two section of walls, NoPossibleSolutionFromCurrentStateError is
        raised.
        """
        board_details = [
            '1,_,W,W',
            'W,O,W,W',
            '_,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_two_by_two_section_of_walls()


class TestCheckForIsolatedWalls(TestBoardStateChecker):
    def test_no_wall_cells(self) -> None:
        """Ensure that when there are no walls, NoPossibleSolutionFromCurrentStateError is not raised."""
        board_details = [
            '1,_,_,_',
            '_,_,_,O',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_isolated_walls()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_isolated_walls() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_one_wall_cell(self) -> None:
        """Ensure that when there is one wall cell, NoPossibleSolutionFromCurrentStateError is not raised."""
        board_details = [
            '1,_,_,_',
            '_,_,_,O',
            '_,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_isolated_walls()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_isolated_walls() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_no_isolation(self) -> None:
        """Ensure that when there are no isolated walls, NoPossibleSolutionFromCurrentStateError is not raised."""
        board_details = [
            '1,_,_,W',
            'W,_,W,_',
            '_,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_isolated_walls()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_isolated_walls() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_single_isolated_wall(self) -> None:
        """Check that when a single wall is isolated, NoPossibleSolutionFromCurrentStateError is raised."""
        board_details = [
            '1,_,_,W',
            'W,O,W,_',
            '_,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_isolated_walls()

    def test_multiple_isolated_wall(self) -> None:
        """Check that when a single wall is isolated, NoPossibleSolutionFromCurrentStateError is raised."""
        board_details = [
            '1,_,_,W',
            'W,O,W,_',
            'W,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_isolated_walls()


class TestCheckForGardenWithMultipleClues(TestBoardStateChecker):
    def test_no_multiple_clue_gardens(self) -> None:
        """
        Ensure that when there are no gardens with multiple clues, NoPossibleSolutionFromCurrentStateError is not
        raised.
        """
        board_details = [
            'O,_,_,_',
            '1,_,_,_',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_garden_with_multiple_clues()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_garden_with_multiple_clues() raised NoPossibleSolutionFromCurrentStateError '
                      'unexpectedly')

    def test_has_multiple_clue_gardens(self) -> None:
        """Check that when there is a garden with multiple clues, NoPossibleSolutionFromCurrentStateError is raised."""
        board_details = [
            'O,_,_,_',
            '1,O,_,_',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_garden_with_multiple_clues()


class TestCheckForTooSmallGarden(TestBoardStateChecker):
    def test_no_too_small_gardens(self) -> None:
        """
        Ensure that when there are no gardens that are too small, NoPossibleSolutionFromCurrentStateError is not raised.
        """
        board_details = [
            '_,_,O,_',
            '1,_,_,_',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_too_small_garden()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_too_small_garden() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_has_too_small_garden(self) -> None:
        """Check that when there is a garden that is too small, NoPossibleSolutionFromCurrentStateError is raised."""
        board_details = [
            '_,_,O,_',
            '1,W,W,_',
            'W,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_too_small_garden()

    def test_garden_with_no_clue_is_ignored(self) -> None:
        """
        Ensure that an enclosed garden that has no clue does not raise an error when running
        check_for_too_small_garden().
        """
        board_details = [
            '_,W,O,O',
            '1,_,W,W',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_too_small_garden()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_too_small_garden() raised NoPossibleSolutionFromCurrentStateError unexpectedly')


class TestCheckForTooLargeGarden(TestBoardStateChecker):
    def test_no_too_large_gardens(self) -> None:
        """
        Ensure that when there are no gardens that are too large, NoPossibleSolutionFromCurrentStateError is not raised.
        """
        board_details = [
            '_,_,_,2',
            '1,_,O,_',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_too_large_garden()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_too_large_garden() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_has_too_large_garden(self) -> None:
        """Check that when there is a garden that is too large, NoPossibleSolutionFromCurrentStateError is raised."""
        board_details = [
            '_,_,O,_',
            '1,_,O,_',
            'W,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_too_large_garden()

    def test_garden_with_no_clue_is_ignored(self) -> None:
        """
        Ensure that a garden that has no clue does not raise an error when calling check_for_too_large_garden().
        """
        board_details = [
            '_,W,O,O',
            '1,_,W,W',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_too_large_garden()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_too_large_garden() raised NoPossibleSolutionFromCurrentStateError unexpectedly')

    def test_garden_with_multiple_clues_is_ignored(self) -> None:
        """
        Ensure that a garden that has multiple clue does not raise an error when calling check_for_too_large_garden().
        """
        board_details = [
            '_,W,O,O',
            '1,_,_,W',
            'O,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_too_large_garden()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_too_large_garden() raised NoPossibleSolutionFromCurrentStateError unexpectedly')


class TestCheckForEnclosedGardenWithNoClue(TestBoardStateChecker):
    def test_no_clueless_enclosed_garden(self) -> None:
        """
        Ensure that when there are no enclosed gardens without a clue, NoPossibleSolutionFromCurrentStateError is not
        raised.
        """
        board_details = [
            '_,O,W,O',
            '1,_,_,_',
            '_,3,O,_',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        try:
            board_state_checker.check_for_enclosed_garden_with_no_clue()
        except NoPossibleSolutionFromCurrentStateError:
            self.fail('check_for_enclosed_garden_with_no_clue() raised NoPossibleSolutionFromCurrentStateError '
                      'unexpectedly')

    def test_has_clueless_enclosed_garden(self) -> None:
        """
        Check that when there is an enclosed garden that has no clue, NoPossibleSolutionFromCurrentStateError is raised.
        """
        board_details = [
            '_,W,O,O',
            '1,_,W,W',
            'W,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_enclosed_garden_with_no_clue()

    def test_has_clueless_unenclosed_garden(self) -> None:
        """
        Check that when there is a garden that has no clue, even if it is not fully enclosed by walls,
        NoPossibleSolutionFromCurrentStateError is raised if it cannot reach a clue cell since it's blocked by walls.
        """
        board_details = [
            '_,W,O,O',
            '1,_,W,_',
            'W,3,O,W',
        ]
        board_state_checker = self.create_board_state_checker(board_details)
        with self.assertRaises(NoPossibleSolutionFromCurrentStateError):
            board_state_checker.check_for_enclosed_garden_with_no_clue()
