__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T
import itertools
from collections import defaultdict
import math


def compute_origin(pts: T.List[T.Tuple[float, float]]):
    """Compute origin of given points."""
    horizontal = set()
    for i, p1 in enumerate(pts):
        for ii, p2 in enumerate(pts[i+1:]):
            (x1, y1), (x2, y2) = p1, p2
            dot = x1 * x2 + y1 * y2
            l1 = (x1*x1 + y1*y1)**0.5
            l2 = (x2*x2 + y2*y2)**0.5
            θ = math.acos(dot / l1 / l2)
            if abs(θ ) < 0.02:
                horizontal.add(p1)
                horizontal.add(p2)

    pts = set(pts)
    print(pts)
    print(horizontal)



def test_origin():
    pts = [(100, 0), (1000, 0), (100, 50)]
    compute_origin(pts)


if __name__ == "__main__":
    test_origin()
