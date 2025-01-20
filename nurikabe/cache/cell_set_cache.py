from ..cell import Cell


class CellSetCache:
    """
    Facilitate caching of sets of Cells for a given cell state.

    For example, when the board has a specific cell state, this class facilitates caching
    of the set of all wall cells.
    """

    def __init__(self) -> None:
        # dictionary of cell_state_hash -> set[Cell]
        self.cache: dict[int, frozenset[Cell]] = {}

    def add_to_cache(self, cell_state_hash: int, cells: frozenset[Cell]) -> None:
        if cell_state_hash not in self.cache:
            self.cache[cell_state_hash] = cells

    def extract_from_cache(self, cell_state_hash: int) -> frozenset[Cell] | None:
        try:
            return self.cache[cell_state_hash]
        except KeyError:
            return None
