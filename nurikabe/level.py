import csv
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path


class BadLevelSetupError(Exception):
    pass


class Level:
    """
    Basic representation of a Nurikabe level. This is just a list of lists, where each cell value is either a
    positive integer representing a clue or None which indicates an empty cell.
    """
    def __init__(self, level_setup: list[list[Optional[int]]]):
        """level_setup is a 2 dimensional list. Each outer list represents a row."""
        self.level_setup = level_setup
        self.number_of_rows = len(self.level_setup)
        self.number_of_columns = len(self.level_setup[0])

        self.ensure_consistent_number_of_columns()

    def ensure_consistent_number_of_columns(self) -> None:
        """If there is an inconsistent number of columns per row, throw an error."""
        for row in self.level_setup:
            if len(row) != self.number_of_columns:
                raise BadLevelSetupError('Inconsistent number of columns in level setup')

    def get_cell_value(self, row_number: int, col_number: int) -> Optional[int]:
        return self.level_setup[row_number][col_number]

    def __str__(self) -> str:
        """
        Format the level info as a printable string. Ensures that alignment is consistent to handle clues of varying
        number of digits.
        """
        printable_level_info = ''
        largest_clue_num_of_digits = len(str(self.get_largest_clue_value()))
        for row in self.level_setup:
            printable_level_info += ','.join(
                self.format_cell_value(cell_value, largest_clue_num_of_digits) for cell_value in row
            )
            printable_level_info += '\n'
        return printable_level_info

    def get_largest_clue_value(self) -> int:
        largest_clue_value = 0
        for row in self.level_setup:
            for cell_value in row:
                if cell_value is not None and cell_value > largest_clue_value:
                    largest_clue_value = cell_value
        return largest_clue_value

    @staticmethod
    def format_cell_value(cell_value: Optional[int], largest_clue_num_of_digits: int) -> str:
        cell_value_str = '' if cell_value is None else str(cell_value)
        return cell_value_str.rjust(largest_clue_num_of_digits)


class LevelBuilder(ABC):
    @abstractmethod
    def build_level(self) -> Level:
        raise NotImplementedError

    @staticmethod
    def parse_cell_value(cell_value_as_str: str) -> Optional[int]:
        if cell_value_as_str == '':
            return None
        elif cell_value_as_str.isnumeric():
            return int(cell_value_as_str)
        else:
            raise BadLevelSetupError(f'Unexpected character in level setup: {cell_value_as_str}')


class LevelBuilderFromFile(LevelBuilder):
    def __init__(self, level_number: int):
        self.level_number = level_number

    def build_level(self) -> Level:
        level_setup = self.read_level_setup()
        return Level(level_setup)

    def read_level_setup(self) -> list[list[Optional[int]]]:
        level_filename = self.get_level_filename()
        with level_filename.open(mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            return [[self.parse_cell_value(value) for value in row] for row in csv_reader]

    def get_level_filename(self) -> Path:
        return Path(__file__).parent / f'levels/level_{self.level_number}.csv'


class LevelBuilderFromStringList(LevelBuilder):
    def __init__(self, level_details: list[str]):
        self.level_details = level_details

    def build_level(self) -> Level:
        level_setup = [[self.parse_cell_value(value) for value in row.split(',')] for row in self.level_details]
        return Level(level_setup)
