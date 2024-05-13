from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cell import Cell
    from ..cell_group import CellGroup


class PathInfo:
    def __init__(self, cell_list: list[Cell], path_length: int, adjacent_cell_groups: set[CellGroup] | None = None):
        self.cell_list = cell_list
        self.path_length = path_length
        self.adjacent_cell_groups = adjacent_cell_groups
        if self.adjacent_cell_groups is None:
            self.adjacent_cell_groups: set[CellGroup] = set()

    def add_adjacent_to_cell_group(self, cell_group: CellGroup) -> None:
        self.adjacent_cell_groups.add(cell_group)

    def get_extended_path_info(self, new_cell: Cell, additional_path_length: int,
                               additional_adjacent_cell_groups: set[CellGroup]) -> PathInfo:
        return PathInfo(
            cell_list=[*self.cell_list, new_cell],
            path_length=self.path_length + additional_path_length,
            adjacent_cell_groups=self.adjacent_cell_groups.union(additional_adjacent_cell_groups),
        )
