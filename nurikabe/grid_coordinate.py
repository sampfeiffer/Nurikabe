from __future__ import annotations

from .direction import Direction, OFFSET_MAP


class GridCoordinate:
    def __init__(self, row_number: int, col_number: int):
        self.row_number = row_number
        self.col_number = col_number

    def get_offset(self, direction: Direction) -> GridCoordinate:
        grid_offset = OFFSET_MAP[direction]
        return GridCoordinate(self.row_number + grid_offset.row_offset, self.col_number + grid_offset.col_offset)
