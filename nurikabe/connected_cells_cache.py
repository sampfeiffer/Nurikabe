import time
from typing import Callable

from .cell import Cell


class FloodFill:
    def __init__(self):
        # dictionary of hash(cell_criteria_func) -> cell_state_hash -> Cell -> connected_cells
        self.cache: dict[int, dict[int, dict[Cell, set[Cell]]]] = {}
        self.connected_cells_native_times = []
        self.connected_cells_recursive_times = []
        self.found_in_cache_count = 0

    # def __del__(self):
    #     print(f'\nNATIVE: number of calls: {len(self.connected_cells_native_times)}')
    #     print(f'NATIVE: total time of calls: {sum(self.connected_cells_native_times)}')
    #     print(
    #         f'NATIVE: avg time of calls: {sum(self.connected_cells_native_times) / len(self.connected_cells_native_times)}')
    #
    #     print(f'\nRECURSIVE: number of calls: {len(self.connected_cells_recursive_times)}')
    #     print(f'RECURSIVE: total time of calls: {sum(self.connected_cells_recursive_times)}')
    #     print(
    #         f'RECURSIVE: avg time of calls: {sum(self.connected_cells_recursive_times) / len(self.connected_cells_recursive_times)}')
    #
    #     print(f'\nfound in cache count: {self.found_in_cache_count}')

    def get_connected_cells(self, cell_state_hash: int, starting_cell: Cell,
                            cell_criteria_func: Callable[[Cell], bool]) -> set[Cell]:
        cell_criteria_func_hash = hash(cell_criteria_func)
        print(f'{cell_state_hash=}, {cell_criteria_func_hash=}, {starting_cell=}')
        if cell_criteria_func_hash not in self.cache:
            self.cache[cell_criteria_func_hash] = {}

        if cell_state_hash not in self.cache[cell_criteria_func_hash]:
            self.cache[cell_criteria_func_hash][cell_state_hash] = {}

        if starting_cell in self.cache[cell_criteria_func_hash][cell_state_hash]:
            self.found_in_cache_count += 1
            return self.cache[cell_criteria_func_hash][cell_state_hash][starting_cell]

        connected_cells = self.calc_connected_cells(starting_cell, cell_criteria_func)
        for cell in connected_cells:
            self.cache[cell_criteria_func_hash][cell_state_hash][cell] = connected_cells
        return connected_cells

    def calc_connected_cells(self, starting_cell: Cell, cell_criteria_func: Callable[[Cell], bool],
                             connected_cells: set[Cell] | None = None) -> set[Cell]:
        """
        Get a list of cells that are connected (non-diagonally) to the starting cell where the cell_criteria_func
        returns True.
        """

        is_native = connected_cells is None
        st = time.time()

        if connected_cells is None:
            connected_cells = set()
        if starting_cell in connected_cells:
            # Already visited this cell
            et = time.time()
            if is_native:
                self.connected_cells_native_times.append(et - st)
            else:
                self.connected_cells_recursive_times.append(et - st)
            return connected_cells
        if cell_criteria_func(starting_cell):
            connected_cells.add(starting_cell)
            for neighbor_cell in starting_cell.get_adjacent_neighbors():
                self.calc_connected_cells(neighbor_cell, cell_criteria_func, connected_cells)

        et = time.time()
        if is_native:
            self.connected_cells_native_times.append(et - st)
        else:
            self.connected_cells_recursive_times.append(et - st)
        return connected_cells
