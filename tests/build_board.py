from nurikabe.level import Level, LevelBuilderFromStringList
from nurikabe.board import Board
from nurikabe.screen import Screen
from nurikabe.cell_state import CellState


def build_board(screen: Screen, board_details: list[str]) -> Board:
    """
    board_details is a list of strings where each string represents one row of the board. For example,
    [
        '_,_,4,O',
        '_,X,X,_',
        '_,1,_,_'
    ]

    '_' indicates an empty cell
    'X' indicates a cell marked as a wall
    'O' indicates a cell marked as a non-wall
    A number indicates a cell with clue equaling that number.
    """

    level = create_level_from_string_list(extract_level_details(board_details))
    board = Board(level, screen)

    for row_number, row in enumerate(board_details):
        cells = row.split(',')
        for col_number, cell_text in enumerate(cells):
            cell = board.get_cell_from_grid(row_number, col_number)
            if cell_text == 'X':
                cell.update_cell_state(CellState.WALL)
            elif cell_text == 'O':
                cell.update_cell_state(CellState.NON_WALL)

    return board


def create_level_from_string_list(level_details: list[str]) -> Level:
    return LevelBuilderFromStringList(level_details).build_level()


def extract_level_details(board_details: list[str]) -> list[str]:
    return [
        row.replace('_', '').replace('X', '').replace('O', '')
        for row in board_details
    ]
