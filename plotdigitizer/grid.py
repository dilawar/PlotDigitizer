__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from pathlib import Path
import cv2 as cv
import numpy as np

import tempfile

TEMP = tempfile.gettempdir()


def _save_fig(img, outfile):
    cv.imwrite(outfile, img)


def remove_horizontal_grid(img) -> np.ndarray:
    μ, σ = img.mean(), img.std()
    for i, row in enumerate(img):
        if row.mean() < μ - σ:
            # I can simply remove the row.
            img[i, :] = img.max()
    return img


def remove_grid(orig) -> np.ndarray:
    img = orig.copy()
    img = remove_horizontal_grid(img)
    return remove_horizontal_grid(img.T).T


def test_remove_grid(imgfile: Path, debug: bool = False):
    img = cv.imread(str(imgfile), 0)
    if debug:
        _save_fig(img, f"{TEMP}/orig.png")
    withoutgrid = remove_grid(img)
    assert withoutgrid.mean() > img.mean()
    if debug:
        _save_fig(withoutgrid, f"{TEMP}/without_grid.png")


if __name__ == "__main__":
    sdir = Path(__file__).parent
    test_remove_grid(sdir / "../figures/graph_with_grid.png")
