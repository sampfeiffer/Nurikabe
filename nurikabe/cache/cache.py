from .cell_groups_cache import CellGroupsCache
from .cell_set_cache import CellSetCache
from .connected_cells_cache import ConnectedCellsCache


class Cache:
    """
    Handles caching of expensive calculations that are potentially called many times for a given state of the board.
    """

    def __init__(self) -> None:
        self.cell_groups_cache = CellGroupsCache()
        self.connected_cells_cache = ConnectedCellsCache()
        self.cell_set_cache = CellSetCache()
