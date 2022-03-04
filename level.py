import csv
from typing import Optional
from pathlib import Path


class Level:
    def __init__(self, level_number: int):
        self.level_number = level_number
        self.level_setup = self.read_level_setup()
        self.number_of_columns = len(self.level_setup[0])
        self.number_of_rows = len(self.level_setup)

    def read_level_setup(self) -> list[list[Optional[int]]]:
        level_filename = self.get_level_filename()
        with level_filename.open(mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            return [[self.parse_cell_value(value) for value in row] for row in csv_reader]

    def get_level_filename(self) -> Path:
        return Path(__file__).parent / f'levels/level_{self.level_number}.csv'

    @staticmethod
    def parse_cell_value(cell_value_as_str: str) -> Optional[int]:
        if cell_value_as_str == '':
            return None
        else:
            return int(cell_value_as_str)

    def get_cell_value(self, row_number: int, col_number: int) -> Optional[int]:
        return self.level_setup[row_number][col_number]

    def __str__(self) -> str:
        # TODO print nicer alignment when there are numbers with multiple digits
        printable_level_info = ''
        for row in self.level_setup:
            printable_level_info += ','.join((' ' if value is None else str(value)) for value in row)
            printable_level_info += '\n'
        return printable_level_info
