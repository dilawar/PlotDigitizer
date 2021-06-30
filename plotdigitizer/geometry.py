__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T
import statistics
import math

def find_origin(pts: T.List[T.Tuple[float, float]]) -> T.Tuple[int, int]:
    """Compute origin of given points."""
    horizontal = set()
    for i, p1 in enumerate(pts):
        for ii, p2 in enumerate(pts[i + 1 :]):
            (x1, y1), (x2, y2) = p1, p2
            if abs(x1 - x2) <= 2:
                continue
            m = (y2 - y1) / (x2 - x1)
            if abs(m) < math.tan(math.pi/180*5):   # <5 deg is horizontal.
                horizontal.add(p1)
                horizontal.add(p2)

    points = set(pts)
    assert len(horizontal) > 1, f"Must have at least two colinear points {horizontal}"
    verticals = points - horizontal
    assert len(verticals) > 0, f"Must be at least one vertical point"
    originY = statistics.mean([x[1] for x in horizontal])
    originX = statistics.mean([x[0] for x in verticals])
    return int(originX), int(originY)


def test_origin():
    pts = [(81, 69), (1779, 68), (81, 449)]
    x, y = find_origin(pts)
    print(pts, '->', (x, y))
    assert (x, y) == (81, 68), (x, y)

    pts = [(23, 26), (140, 23), (22, 106)]
    x, y = find_origin(pts)
    print(pts, '->', (x, y))
    assert (x, y) == (22, 24), (x, y)

    pts = [(2, 12), (897, 12), (2, 183)]
    x, y = find_origin(pts)
    assert (x, y) == (2, 12), (x, y)
    print(pts, '->', (x, y))


if __name__ == "__main__":
    test_origin()
