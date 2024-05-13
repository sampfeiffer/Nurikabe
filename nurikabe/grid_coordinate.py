from __future__ import annotations

from .direction import OFFSET_MAP, Direction


class GridCoordinate:
    def __init__(self, row_number: int, col_number: int):
        self.row_number = row_number
        self.col_number = col_number

    def get_offset(self, direction: Direction) -> GridCoordinate:
        grid_offset = OFFSET_MAP[direction]
        return GridCoordinate(self.row_number + grid_offset.row_offset, self.col_number + grid_offset.col_offset)

    def __repr__(self) -> str:
        return f'GridCoordinate(row_number={self.row_number}, col_number={self.col_number})'
