"""Spatial contract for a bounded, reversible window proxy.

The renderer may rearrange rectangular regions only when each destination
region has one and only one source region.  This is the smallest interaction
contract: render with T and route a proxy coordinate back with T^-1.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuadrantPermutation:
    """Maps each destination quadrant to the source quadrant it displays."""

    destination_to_source: tuple[int, int, int, int]

    def __post_init__(self) -> None:
        values = self.destination_to_source
        if len(values) != 4 or set(values) != {0, 1, 2, 3}:
            raise ValueError("window proxy requires a bijection of four regions")

    def source_to_destination(self, source_quadrant: int) -> int:
        if source_quadrant not in range(4):
            raise ValueError("unknown source quadrant")
        return self.destination_to_source.index(source_quadrant)

    @staticmethod
    def quadrant(x: int, y: int, size: int) -> tuple[int, int, int]:
        if size <= 1 or not 0 <= x < size or not 0 <= y < size:
            raise ValueError("point is outside the proxy surface")
        half = size // 2
        quadrant = (1 if x >= half else 0) + (2 if y >= half else 0)
        return quadrant, x % half, y % half

    def proxy_to_source(self, x: int, y: int, size: int) -> tuple[int, int]:
        destination, local_x, local_y = self.quadrant(x, y, size)
        source = self.destination_to_source[destination]
        half = size // 2
        return (source % 2) * half + local_x, (source // 2) * half + local_y

    def source_to_proxy(self, x: int, y: int, size: int) -> tuple[int, int]:
        source, local_x, local_y = self.quadrant(x, y, size)
        destination = self.source_to_destination(source)
        half = size // 2
        return (destination % 2) * half + local_x, (destination // 2) * half + local_y


DEFAULT_PERMUTATION = QuadrantPermutation((3, 2, 1, 0))
