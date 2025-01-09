from .cell_group import CellGroup


class CellGroupsCache:
    def __init__(self):
        # dictionary of valid_cells_hash -> cell_state_hash -> set[CellGroup]
        self.cache: dict[int, dict[int, set[CellGroup]]] = {}

    def add_to_cache(self, valid_cells_hash: int, cell_state_hash: int, all_cell_groups: set[CellGroup]) -> None:
        if valid_cells_hash not in self.cache:
            self.cache[valid_cells_hash] = {}

        if cell_state_hash not in self.cache[valid_cells_hash]:
            self.cache[valid_cells_hash][cell_state_hash] = all_cell_groups


    def extract_from_cache(self, valid_cells_hash: int, cell_state_hash: int) -> set[CellGroup] | None:
        try:
            return self.cache[valid_cells_hash][cell_state_hash]
        except KeyError:
            return None
