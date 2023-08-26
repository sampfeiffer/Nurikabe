from unittest import TestCase

from nurikabe.level import LevelBuilderFromStringList, BadLevelSetupError


class TestLevelBuilder(TestCase):
    def test_correctly_formatted_level_details(self) -> None:
        """When the level details list is properly formatted, a Level object is properly created."""
        level_details = [
            ',,3,',
            ',,,',
            ',1,,'
        ]
        try:
            LevelBuilderFromStringList(level_details).build_level()
        except BadLevelSetupError:
            self.fail('LevelBuilderFromStringList.build_level() raised BadLevelSetupError unexpectedly')

    def test_inconsistent_num_of_columns_per_row(self) -> None:
        """If there is an inconsistent number of columns per row in the level details, an error should be thrown."""
        level_details = [
            ',,3',
            ',,',
            ',1,,'
        ]
        with self.assertRaises(BadLevelSetupError):
            LevelBuilderFromStringList(level_details).build_level()

    def test_unexpected_character(self) -> None:
        """If there is an unexpected character in the level details, an error should be thrown."""
        level_details = [
            ',,3',
            ',,e',
            ',1,,'
        ]
        with self.assertRaises(BadLevelSetupError):
            LevelBuilderFromStringList(level_details).build_level()
