from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cell_state import CellState
    from .grid_coordinate import GridCoordinate


@dataclass(frozen=True)
class CellStateChange:
    before_state: CellState
    after_state: CellState

    def is_wall_change(self) -> bool:
        return self.before_state.is_wall() or self.after_state.is_wall()


class CellChangeInfo:
    def __init__(self, grid_coordinate: GridCoordinate, before_state: CellState, after_state: CellState, reason: str):
        self.grid_coordinate = grid_coordinate
        self.cell_state_change = CellStateChange(before_state, after_state)
        self.reason = reason

    def is_wall_change(self) -> bool:
        return self.cell_state_change.is_wall_change()

    def get_reversed_change(self) -> CellChangeInfo:
        """Useful for undoing changes."""
        return CellChangeInfo(
            grid_coordinate=self.grid_coordinate,
            before_state=self.cell_state_change.after_state,
            after_state=self.cell_state_change.before_state,
            reason=f'reverse {self.reason}',
        )


class CellChanges:
    def __init__(self, cell_change_list: list[CellChangeInfo] | None = None):
        self.cell_change_list: list[CellChangeInfo] = []
        if cell_change_list is not None:
            self.cell_change_list = cell_change_list

    def add_change(self, cell_change_info: CellChangeInfo) -> None:
        self.cell_change_list.append(cell_change_info)

    def add_changes(self, cell_changes: CellChanges) -> None:
        self.cell_change_list.extend(cell_changes.cell_change_list)

    def has_any_changes(self) -> bool:
        return len(self.cell_change_list) > 0

    def get_reversed_changes(self) -> CellChanges:
        """Useful for undoing changes."""
        cell_change_list = [cell_change_info.get_reversed_change() for cell_change_info in self.cell_change_list]
        return CellChanges(cell_change_list)

    def has_any_wall_changes(self) -> bool:
        return any(cell_change_info.is_wall_change() for cell_change_info in self.cell_change_list)

    def get_unique_cell_state_changes(self) -> frozenset[CellStateChange]:
        return frozenset({cell_change_info.cell_state_change for cell_change_info in self.cell_change_list})
