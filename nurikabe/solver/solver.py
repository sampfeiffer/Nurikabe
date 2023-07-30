import logging

from ..screen import Screen
from ..board import Board
from ..cell import Cell
from ..color import Color
from ..cell_change_info import CellChanges
from ..undo_redo_control import UndoRedoControl
from .board_state_checker import BoardStateChecker

from .solver_rules.separate_clues import SeparateClues
from .solver_rules.no_isolated_wall_sections import NoIsolatedWallSections
from .solver_rules.ensure_garden_can_expand import EnsureGardenCanExpand
from .solver_rules.enclose_full_garden import EncloseFullGarden
from .solver_rules.ensure_no_two_by_two_walls import EnsureNoTwoByTwoWalls
from .solver_rules.naively_unreachable_from_clue_cell import NaivelyUnreachableFromClueCell
from .solver_rules.naively_unreachable_from_garden import NaivelyUnreachableFromGarden
from .solver_rules.separate_gardens_with_clues import SeparateGardensWithClues
from .solver_rules.fill_correctly_sized_weak_garden import FillCorrectlySizedWeakGarden
from .solver_rules.unreachable_from_garden import UnreachableFromGarden

logger = logging.getLogger(__name__)


class Solver:
    def __init__(self, screen: Screen, board: Board, undo_redo_control: UndoRedoControl):
        self.screen = screen
        self.board = board
        self.undo_redo_control = undo_redo_control

        self.board_state_checker = BoardStateChecker(self.board)

        # Solver rules
        self.separate_clues = SeparateClues(self.board)
        self.no_isolated_wall_sections = NoIsolatedWallSections(self.board)
        self.ensure_garden_can_expand = EnsureGardenCanExpand(self.board)
        self.enclose_full_garden = EncloseFullGarden(self.board)
        self.ensure_no_two_by_two_walls = EnsureNoTwoByTwoWalls(self.board)
        self.naively_unreachable_from_clue_cell = NaivelyUnreachableFromClueCell(self.board)
        self.naively_unreachable_from_garden = NaivelyUnreachableFromGarden(self.board)
        self.separate_gardens_with_clues = SeparateGardensWithClues(self.board)
        self.fill_correctly_sized_weak_garden = FillCorrectlySizedWeakGarden(self.board)
        self.unreachable_from_garden = UnreachableFromGarden(self.board)

    def run_solver(self) -> CellChanges:
        cell_changes = CellChanges()

        self.board_state_checker.check_for_board_state_issue()

        cell_changes.add_changes(self.separate_clues.apply_rule())
        cell_changes.add_changes(self.no_isolated_wall_sections.apply_rule())
        cell_changes.add_changes(self.ensure_garden_can_expand.apply_rule())
        cell_changes.add_changes(self.enclose_full_garden.apply_rule())
        cell_changes.add_changes(self.ensure_no_two_by_two_walls.apply_rule())
        cell_changes.add_changes(self.naively_unreachable_from_clue_cell.apply_rule())
        cell_changes.add_changes(self.naively_unreachable_from_garden.apply_rule())
        cell_changes.add_changes(self.separate_gardens_with_clues.apply_rule())
        cell_changes.add_changes(self.fill_correctly_sized_weak_garden.apply_rule())
        cell_changes.add_changes(self.unreachable_from_garden.apply_rule())

        self.board.update_painted_gardens()
        self.undo_redo_control.process_board_event(cell_changes)
        return cell_changes



    def color_group(self, cells: set[Cell]) -> None:
        for cell in cells:
            cell.draw_perimeter(Color.YELLOW)
        self.screen.update_screen()
