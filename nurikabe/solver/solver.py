import logging
import time

from ..board import Board
from ..cell_change_info import CellChanges
from ..color import Color
from ..screen import Screen
from ..undo_redo_control import UndoRedoControl
from .board_state_checker import BoardStateChecker, NoPossibleSolutionFromCurrentStateError
from .solver_rules.enclose_full_garden import EncloseFullGarden
from .solver_rules.ensure_garden_can_expand_one_route import EnsureGardenCanExpandOneRoute
from .solver_rules.ensure_garden_with_clue_can_expand import EnsureGardenWithClueCanExpand
from .solver_rules.ensure_garden_without_clue_can_expand import EnsureGardenWithoutClueCanExpand
from .solver_rules.ensure_no_two_by_two_walls import EnsureNoTwoByTwoWalls
from .solver_rules.fill_correctly_sized_weak_garden import FillCorrectlySizedWeakGarden
from .solver_rules.naively_unreachable_from_clue_cell import NaivelyUnreachableFromClueCell
from .solver_rules.naively_unreachable_from_garden import NaivelyUnreachableFromGarden
from .solver_rules.no_isolated_wall_sections import NoIsolatedWallSections
from .solver_rules.no_isolated_wall_sections_naive import NoIsolatedWallSectionsNaive
from .solver_rules.separate_clues import SeparateClues
from .solver_rules.separate_gardens_with_clues import SeparateGardensWithClues
from .solver_rules.unreachable_from_garden import UnreachableFromGarden

logger = logging.getLogger(__name__)


class Solver:
    def __init__(self, screen: Screen, board: Board, undo_redo_control: UndoRedoControl):
        self.screen = screen
        self.board = board
        self.undo_redo_control = undo_redo_control

        self.board_state_checker = BoardStateChecker(self.board)

        self.solver_rules = frozenset({
            SeparateClues(self.board),
            EnsureGardenCanExpandOneRoute(self.board),
            EnsureNoTwoByTwoWalls(self.board),
            NaivelyUnreachableFromClueCell(self.board),
            EncloseFullGarden(self.board),
            NoIsolatedWallSectionsNaive(self.board),
            FillCorrectlySizedWeakGarden(self.board),
            SeparateGardensWithClues(self.board),
            NaivelyUnreachableFromGarden(self.board),
            EnsureGardenWithoutClueCanExpand(self.board),
            EnsureGardenWithClueCanExpand(self.board),
            UnreachableFromGarden(self.board),
            NoIsolatedWallSections(self.board)
        })

    def run_solver(self) -> CellChanges:
        self.board_state_checker.check_for_board_state_issue()
        cell_changes = CellChanges()
        # changes_per_run = []
        start_time = time.time()

        solver_rules_to_run = sorted(self.solver_rules, key=lambda solver_rule: solver_rule.rule_cost)
        cell_changes_since_last_solver_run = CellChanges()

        saturated_rule = None

        while len(solver_rules_to_run) > 0 or len(cell_changes_since_last_solver_run.cell_change_list) > 0:
        # first_run = True
        # while first_run or len(cell_changes_since_last_solver_run.cell_change_list) > 0:
            first_run = False
            rules_not_in_current_queue = self.solver_rules - set(solver_rules_to_run)
            potential_rules_to_add = {rule for rule in rules_not_in_current_queue if rule != saturated_rule}
            unique_cell_state_changes = cell_changes_since_last_solver_run.get_unique_cell_state_changes()
            rules_to_add_to_queue = {rule for rule in potential_rules_to_add if rule.should_trigger_rule(unique_cell_state_changes)}
            ordered_rules_to_add_to_queue = sorted(rules_to_add_to_queue, key=lambda solver_rule: solver_rule.rule_cost)
            logger.debug(f"Add to queue: {[rule.__class__ for rule in ordered_rules_to_add_to_queue]}")
            solver_rules_to_run.extend(ordered_rules_to_add_to_queue)
            #
            logger.debug(f"number of rules in queue {len(solver_rules_to_run)}")
            # # breakpoint()
            cell_changes_since_last_solver_run = CellChanges()

            try:
                if len(solver_rules_to_run) == 0:
                    break

                rule_to_run = solver_rules_to_run[0]
                # for rule_to_run in solver_rules_to_run:
                logger.debug(f"running rule {rule_to_run.__class__}")
                cell_changes_since_last_solver_run.add_changes(rule_to_run.apply_rule())
                if cell_changes_since_last_solver_run.has_any_changes():
                    if rule_to_run.is_saturating_rule:
                        saturated_rule = rule_to_run
                        solver_rules_to_run.remove(rule_to_run)
                    else:
                        saturated_rule = None
                else:
                    solver_rules_to_run.remove(rule_to_run)

                # changes_per_run.append(cell_changes_since_last_solver_run)
                cell_changes.add_changes(cell_changes_since_last_solver_run)
                # logger.debug(cell_changes_since_last_solver_run.get_unique_cell_state_changes())
                # self.board.update_painted_gardens()
            except NoPossibleSolutionFromCurrentStateError as error:
                logger.exception('Cannot solve from current state')
                for cell_group in error.problem_cell_groups:
                    cell_group.draw_edges(self.screen, color=Color.RED)

        self.board.update_painted_gardens()
        end_time = time.time()
        total_time = 1000 * (end_time - start_time)
        logger.debug(f'total solve time in milliseconds: {total_time:.1f}')
        # self.print_stats(changes_per_run)
        self.undo_redo_control.process_board_event(cell_changes)
        return cell_changes

    def print_stats(self, changes_per_run: list[CellChanges]) -> None:

        # changes_per_run_dict: dict[str, list[int]] = {}
        changes_per_run_list: list[dict[str, int]] = [{} for _ in range(len(changes_per_run))]
        for run_number, run in enumerate(changes_per_run):
            for cell_change in run.cell_change_list:
                reason = cell_change.reason
                if reason not in changes_per_run_list[run_number]:
                    changes_per_run_list[run_number][reason] = 0
                changes_per_run_list[run_number][reason] += 1
        print(changes_per_run_list)
        unique_reasons = set()
        for changes_dict in changes_per_run_list:
            unique_reasons.update(changes_dict.keys())

        res = {reason: [] for reason in unique_reasons}
        for changes_dict in changes_per_run_list:
            for reason in unique_reasons:
                res[reason].append(changes_dict.get(reason, 0))

        print(res)
        import pandas as pd
        res_df = pd.DataFrame(res)
        res_df.to_csv('solver_rule_stats.csv')
