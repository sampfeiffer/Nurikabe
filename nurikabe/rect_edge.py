from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .pixel_position import PixelPosition

if TYPE_CHECKING:
    import pygame


@dataclass(frozen=True)
class RectEdge:
    """Represents the edge of a pygame.Rect object."""

    start_pixel_position: PixelPosition
    end_pixel_position: PixelPosition

    def __str__(self) -> str:
        return f'RectEdge({self.start_pixel_position}, {self.end_pixel_position})'

    def __eq__(self, other_rect_edge: object) -> bool:
        """Accounts for the fact that the edge a-b is the same as the edge b-a."""
        if not isinstance(other_rect_edge, RectEdge):
            return NotImplemented
        return (
            self.start_pixel_position == other_rect_edge.start_pixel_position
            and self.end_pixel_position == other_rect_edge.end_pixel_position
        ) or (
            self.start_pixel_position == other_rect_edge.end_pixel_position
            and self.end_pixel_position == other_rect_edge.start_pixel_position
        )


def get_rect_edges(rect: pygame.Rect) -> set[RectEdge]:
    """Get all four edges of a pygame.Rect object."""
    left_edge = RectEdge(
        PixelPosition(x_coordinate=rect.left, y_coordinate=rect.top),
        PixelPosition(x_coordinate=rect.left, y_coordinate=rect.bottom),
    )
    right_edge = RectEdge(
        PixelPosition(x_coordinate=rect.right, y_coordinate=rect.top),
        PixelPosition(x_coordinate=rect.right, y_coordinate=rect.bottom),
    )
    top_edge = RectEdge(
        PixelPosition(x_coordinate=rect.left, y_coordinate=rect.top),
        PixelPosition(x_coordinate=rect.right, y_coordinate=rect.top),
    )
    bottom_edge = RectEdge(
        PixelPosition(x_coordinate=rect.left, y_coordinate=rect.bottom),
        PixelPosition(x_coordinate=rect.right, y_coordinate=rect.bottom),
    )
    return {left_edge, right_edge, top_edge, bottom_edge}
