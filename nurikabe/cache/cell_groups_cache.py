from nurikabe.cell_group import CellGroup


class CellGroupsCache:
    """
    Facilitate caching of sets of CellGroups for a given set of valid cells and a given cell state.

    For example, given the set of a wall cells when the board has a specific cell state, this class facilitates caching
    of the set of each wall group.
    """

    def __init__(self) -> None:
        # dictionary of cell_state_hash -> valid_cells_hash -> set[CellGroup]
        self.cache: dict[int, dict[int, frozenset[CellGroup]]] = {}

    def add_to_cache(self, cell_state_hash: int, valid_cells_hash: int, all_cell_groups: frozenset[CellGroup]) -> None:
        if cell_state_hash not in self.cache:
            self.cache[cell_state_hash] = {}

        if valid_cells_hash not in self.cache[cell_state_hash]:
            self.cache[cell_state_hash][valid_cells_hash] = all_cell_groups


    def extract_from_cache(self, cell_state_hash: int, valid_cells_hash: int) -> frozenset[CellGroup] | None:
        try:
            return self.cache[cell_state_hash][valid_cells_hash]
        except KeyError:
            return None
