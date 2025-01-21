import string
from dataclasses import dataclass

from nurikabe.board import Board
from nurikabe.cell import Cell
from nurikabe.cell_group import CellGroup
from nurikabe.screen import Screen
from nurikabe.solver.path_finding import PathFinder

from ...build_board import build_board


class BadPathFinderSetupError(Exception):
    pass


@dataclass
class PathFinderInfo:
    board: Board
    path_finder: PathFinder


def build_path_finder(screen: Screen, board_details: list[str]) -> PathFinderInfo:
    """
    Build a PathFinderInfo object from a list of strings.

    board_details is a list of strings where each string represents one row of the board. For example,
    [
        'a,_,S,_',
        '_,X,X,b',
        'a,a,_,b',
        '_,E,E,_',
    ]

    '_' indicates an empty cell
    'S' indicates a cell in the start cell group
    'E' indicates a cell in the end cell group
    'X' indicates an off limit cell
    Lower-case letters indicate other cell groups where each group contains cells of that letter. In the example above,
    there are three cells in cell group 'a' and two cells in cell group 'b'.
    """
    board = build_board(screen=screen, board_details=extract_blank_board_details(board_details))
    start_cell_group: set[Cell] = set()
    end_cell_group: set[Cell] = set()
    off_limit_cells: set[Cell] = set()
    other_cell_group_cells: dict[str, set[Cell]] = {}

    for row_number, row in enumerate(board_details):
        cells = row.split(',')
        for col_number, cell_text in enumerate(cells):
            cell = board.get_cell_from_grid(row_number, col_number)
            if len(cell_text) != 1:
                msg = f'Path finder setup must have a single character per cell. Found: "{cell_text}"'
                raise BadPathFinderSetupError(msg)

            if cell_text == 'S':
                start_cell_group.add(cell)
            elif cell_text == 'E':
                end_cell_group.add(cell)
            elif cell_text == 'X':
                off_limit_cells.add(cell)
            elif cell_text in string.ascii_lowercase:
                if cell_text in other_cell_group_cells:
                    other_cell_group_cells[cell_text].add(cell)
                else:
                    other_cell_group_cells[cell_text] = {cell}
            elif cell_text == '_':
                # Empty cell
                pass
            else:
                msg = f'Unexpected character in path finder setup: {cell_text}'
                raise BadPathFinderSetupError(msg)

    other_cell_groups = {CellGroup(cells) for cells in other_cell_group_cells.values()}

    check_path_endpoints(start_cell_group, end_cell_group)

    path_finder = PathFinder(
        start_cell_group=CellGroup(start_cell_group),
        end_cell_group=CellGroup(end_cell_group),
        off_limit_cells=frozenset(off_limit_cells),
        other_cell_groups=frozenset(other_cell_groups),
    )
    return PathFinderInfo(board, path_finder)


def check_path_endpoints(start_cell_group: set[Cell], end_cell_group: set[Cell]) -> None:
    if len(start_cell_group) == 0:
        msg = 'Start cell group must contain at least one cell'
        raise BadPathFinderSetupError(msg)
    if len(end_cell_group) == 0:
        msg = 'End cell group must contain at least one cell'
        raise BadPathFinderSetupError(msg)


def extract_blank_board_details(board_details: list[str]) -> list[str]:
    return [','.join(['_' for _ in row_details.split(',')]) for row_details in board_details]
