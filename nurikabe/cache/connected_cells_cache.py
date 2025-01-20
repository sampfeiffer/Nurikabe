from ..cell import Cell


class ConnectedCellsCache:
    """
    Facilitate caching of sets of connected cell sets for a given set of valid cells, given starting cell and a given
    cell state.

    i.e. This functions as a flood fill cache.
    """

    def __init__(self) -> None:
        # dictionary of cell_state_hash -> valid_cells_hash -> starting_cell -> frozenset[Cell]
        self.cache: dict[int, dict[int, dict[Cell, frozenset[Cell]]]] = {}

    def add_to_cache(
        self, cell_state_hash: int, valid_cells_hash: int, starting_cell: Cell, connected_cells: frozenset[Cell]
    ) -> None:
        if cell_state_hash not in self.cache:
            self.cache[cell_state_hash] = {}

        if valid_cells_hash not in self.cache[cell_state_hash]:
            self.cache[cell_state_hash][valid_cells_hash] = {}

        if starting_cell not in self.cache[cell_state_hash][valid_cells_hash]:
            for cell in connected_cells:
                self.cache[cell_state_hash][valid_cells_hash][cell] = connected_cells

    def extract_from_cache(
        self, cell_state_hash: int, valid_cells_hash: int, starting_cell: Cell
    ) -> frozenset[Cell] | None:
        try:
            return self.cache[cell_state_hash][valid_cells_hash][starting_cell]
        except KeyError:
            return None
