#!/usr/bin/env python3

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

from pathlib import Path
import logging
import numpy as np
import math
import cv2

WINDOW_NAME = "PlotDigitizer: Click on a point to find coordinates."

img_: np.ndarray = np.zeros((1, 1))


def _locate_points(k, x, y, s, p):
    global img_
    if k == 4:
        logging.info(f"You clicked on {x}/{y}")
        _add_point(x, y)


def _draw_cross(x, y, r, color=10):
    global img_
    _cos45, _sin45 = math.sin(math.pi / 4), math.cos(math.pi / 4)
    cv2.line(
        img_,
        (x - int(r * _cos45), y - int(r * _sin45)),
        (x + int(r * _cos45), y + int(r * _sin45)),
        color,
        1,
    )
    cv2.line(
        img_,
        (x - int(r * _cos45), y + int(r * _sin45)),
        (x + int(r * _cos45), y - int(r * _sin45)),
        color,
        1,
    )


def _add_point(x, y):
    global img_
    W, H = img_.shape
    color = img_.max() - img_.mean()
    txt = f"{x},{W-y}"
    #  cv2.circle(img_, (x, y), max(5, min(H, W) // 100), color, -1)
    _draw_cross(x, y, 15, color)
    cv2.putText(img_, txt, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)


def _add_axis(img):
    H, W = img.shape
    th = 10
    img = np.pad(img, ((0, th), (th, 0)), constant_values=220)
    cv2.putText(img, "0,0", (0, H), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 1)
    return img


def locate(imgfile: Path):
    global img_
    logging.info(f"Loading {imgfile}")
    assert imgfile.is_file(), f"{imgfile} does not exists or could not be read"
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, _locate_points)
    img_ = cv2.imread(str(imgfile), 0)
    #  img_ = _add_axis(img_)
    while cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) > 0:
        cv2.imshow(WINDOW_NAME, img_)
        k = cv2.waitKey(30) & 0xFF
        if k == ord("q"):
            cv2.destroyAllWindows()
            break


def main():
    import argparse

    parser = argparse.ArgumentParser("Find coordinate of points")
    parser.add_argument("INFILE", type=Path, help="Inout file")
    args = parser.parse_args()
    locate(args.INFILE)


if __name__ == "__main__":
    main()
