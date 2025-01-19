from .cell_groups_cache import CellGroupsCache
from .cell_set_cache import CellSetCache

class Cache:
    def __init__(self):
        self.cell_groups_cache = CellGroupsCache()
        self.garden_cells_cache = CellSetCache()
