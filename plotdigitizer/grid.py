__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from pathlib import Path
import cv2 as cv
import numpy as np

import tempfile

TEMP = tempfile.gettempdir()


def _save_fig(img, outfile):
    print(f"Saved to {outfile}")
    cv.imwrite(outfile, img)


def remove_horizontal_grid_simple(img) -> np.ndarray:
    μ, σ = img.mean(), img.std()
    for i, row in enumerate(img):
        if row.mean() < μ - σ:
            # I can simply remove the row.
            img[i, :] = img.max()
    return img


def heal(orig):
    kernel = np.ones((3, 3), np.uint8)
    img = cv.morphologyEx(orig.copy(), cv.MORPH_OPEN, kernel, iterations=2)
    return img


def remove_grid(
    orig, num_iter=3, background_color: int = 255, grid_size: int = 2
) -> np.ndarray:
    img = orig.copy()
    thres = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (40, 1))
    remove_horizontal = cv.morphologyEx(
        thres, cv.MORPH_OPEN, horizontal_kernel, iterations=num_iter
    )
    cnts = cv.findContours(remove_horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv.drawContours(img, [c], -1, background_color, grid_size)

    # Remove vertical lines
    vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 40))
    remove_vertical = cv.morphologyEx(
        thres, cv.MORPH_OPEN, vertical_kernel, iterations=num_iter
    )
    cnts = cv.findContours(remove_vertical, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv.drawContours(img, [c], -1, background_color, grid_size)
    return img


def test_remove_grid(imgfile: Path, debug: bool = True):
    img = cv.imread(str(imgfile), 0)
    if debug:
        _save_fig(img, f"{TEMP}/orig.png")
    withoutgrid = remove_grid(img)
    # assert withoutgrid.mean() > img.mean()
    if debug:
        _save_fig(withoutgrid, f"{TEMP}/without_grid.png")


if __name__ == "__main__":
    sdir = Path(__file__).parent
    test_remove_grid(sdir / "../figures/graph_with_grid.png", True)
