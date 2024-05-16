from enum import Enum
from typing import ClassVar


class Color(Enum):
    BLACK = 3 * [0]
    OFF_WHITE = 3 * [240]
    GRAY = 3 * [160]
    LIGHT_SLATE_GRAY: ClassVar[list[int]] = [178, 204, 229]
    MEDIUM_SLATE_GRAY: ClassVar[list[int]] = [119, 136, 153]
    GREEN: ClassVar[list[int]] = [0, 128, 0]
    RED: ClassVar[list[int]] = [255, 0, 0]
    YELLOW: ClassVar[list[int]] = [255, 255, 0]
