__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T
import statistics
import itertools
from collections import defaultdict
import math


def compute_origin(pts: T.List[T.Tuple[float, float]]):
    """Compute origin of given points."""
    horizontal = set()
    for i, p1 in enumerate(pts):
        for ii, p2 in enumerate(pts[i + 1 :]):
            (x1, y1), (x2, y2) = p1, p2
            if abs(x1 - x2) <= 2:
                continue
            m = (y2 - y1) / (x2 - x1)
            if abs(m) < 0.01:
                horizontal.add(p1)
                horizontal.add(p2)

    points = set(pts)
    assert len(horizontal) > 1, "Must have at least two co-linear points"
    verticals = points - horizontal
    originY = statistics.mean([x[1] for x in horizontal])
    originX = statistics.mean([x[0] for x in verticals])
    return int(originX), int(originY)


def test_origin():
    pts = [(81, 69), (1779, 68), (81, 449)]
    x, y = compute_origin(pts)
    assert (x, y) == (81, 68), (x, y)


if __name__ == "__main__":
    test_origin()
