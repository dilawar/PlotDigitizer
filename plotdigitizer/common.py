# common module

import typing as T
from pathlib import Path
import hashlib
import tempfile

import numpy as np
from plotdigitizer import geometry

WindowName_ = "PlotDigitizer"
ix_, iy_ = 0, 0
params_: T.Dict[str, T.Any] = {}

# NOTE: remember these are cv coordinates and not numpy.
locations_: T.List[geometry.Point] = []
points_: T.List[geometry.Point] = []

img_ = np.zeros((1, 1))

def cache() -> Path:
    c = Path(tempfile.gettempdir()) / "plotdigitizer"
    c.mkdir(parents=True, exist_ok=True)
    return c


def data_to_hash(data) -> str:
    return hashlib.sha1(data).hexdigest()
