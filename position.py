from __future__ import annotations

from direction import Direction, OFFSET_MAP


class Position:
    def __init__(self, x_coordinate: int, y_coordinate: int):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.coordinates = x_coordinate, y_coordinate

    @staticmethod
    def from_tuple(position_tuple: tuple[int, int]) -> Position:
        return Position(position_tuple[0], position_tuple[1])

    def get_offset(self, direction: Direction) -> Position:
        x_offset, y_offset = OFFSET_MAP[direction]
        return Position(self.x_coordinate + x_offset, self.y_coordinate + y_offset)
