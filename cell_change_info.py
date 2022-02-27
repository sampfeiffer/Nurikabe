from dataclasses import dataclass

from cell_state import CellState


@dataclass
class CellChangeInfo:
    before_state: CellState
    after_state: CellState

    def is_wall_change(self) -> bool:
        return self.before_state is CellState.WALL or self.after_state is CellState.WALL
