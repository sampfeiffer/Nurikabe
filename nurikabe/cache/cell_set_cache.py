from ..cell import Cell
from ..cell_state import CellStateCriteriaFunc


class CellSetCache:
    """
    Facilitate caching of sets of Cells for a given cell state.

    For example, when the board has a specific cell state, this class facilitates caching of the set of all wall cells.
    """

    def __init__(self) -> None:
        # dictionary of cell_state_hash -> cell_state_criteria_func -> frozenset[Cell]
        self.cache: dict[int, dict[CellStateCriteriaFunc, frozenset[Cell]]] = {}

    def add_to_cache(
        self, cell_state_hash: int, cell_state_criteria_func: CellStateCriteriaFunc, cells: frozenset[Cell]
    ) -> None:
        if cell_state_hash not in self.cache:
            self.cache[cell_state_hash] = {}

        if cell_state_criteria_func not in self.cache[cell_state_hash]:
            self.cache[cell_state_hash][cell_state_criteria_func] = cells

    def extract_from_cache(
        self, cell_state_hash: int, cell_state_criteria_func: CellStateCriteriaFunc
    ) -> frozenset[Cell] | None:
        try:
            return self.cache[cell_state_hash][cell_state_criteria_func]
        except KeyError:
            return None
