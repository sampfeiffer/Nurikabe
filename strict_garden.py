from garden import Garden


class StrictGarden(Garden):
    """A StrictGarden is a Garden that only includes cells marked as a non-wall and clue cells."""

    def get_num_of_remaining_non_wall_cells(self) -> int:
        expected_garden_size = self.get_expected_garden_size()
        return expected_garden_size - len(self.cells)
