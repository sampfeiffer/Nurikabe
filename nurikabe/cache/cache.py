from .cell_groups_cache import CellGroupsCache
from .cell_set_cache import CellSetCache
from .connected_cells_cache import ConnectedCellsCache


class Cache:
    def __init__(self) -> None:
        self.cell_groups_cache = CellGroupsCache()
        self.connected_cells_cache = ConnectedCellsCache()
        self.garden_cells_cache = CellSetCache()
