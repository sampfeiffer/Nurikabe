from enum import Enum


class Color(Enum):
    BLACK = 3 * [0]
    OFF_WHITE = 3 * [240]
    GRAY = 3 * [160]
    LIGHT_GRAY = 3 * [210]
    LIGHT_SLATE_GRAY = [119, 136, 153]
    GREEN = [0, 128, 0]
    RED = [255, 0, 0]
    YELLOW = [255, 255, 0]
    ORANGE = [255, 165, 0]
    PURPLE = [128, 0, 128]
