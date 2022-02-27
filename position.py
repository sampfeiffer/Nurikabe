from __future__ import annotations


class Position:
    def __init__(self, x_coordinate: int, y_coordinate: int):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.coordinates = x_coordinate, y_coordinate

    @staticmethod
    def from_tuple(position_tuple: tuple[int, int]) -> Position:
        return Position(position_tuple[0], position_tuple[1])
