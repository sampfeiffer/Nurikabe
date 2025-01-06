from .cell_group import CellGroup


class CellGroupsCache:
    def __init__(self):
        # dictionary of hash(cell_criteria_func) -> cell_state_hash -> set[CellGroup]
        self.cache: dict[int, dict[int, set[CellGroup]]] = {}

    def add_to_cache(self, cell_criteria_func_hash: int, cell_state_hash: int, all_cell_groups: set[CellGroup]) -> None:
        if cell_criteria_func_hash not in self.cache:
            self.cache[cell_criteria_func_hash] = {}

        if cell_state_hash not in self.cache[cell_criteria_func_hash]:
            self.cache[cell_criteria_func_hash][cell_state_hash] = all_cell_groups


    def extract_from_cache(self, cell_criteria_func_hash: int, cell_state_hash: int) -> set[CellGroup] | None:
        try:
            return self.cache[cell_criteria_func_hash][cell_state_hash]
        except KeyError:
            return None
