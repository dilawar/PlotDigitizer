#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2017-, Dilawar Singh"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"
__status__ = "Development"

import sys
import typing as T
import numpy as np
import hashlib
from pathlib import Path
import cv2
import tempfile
from collections import defaultdict
from loguru import logger

WindowName_ = "PlotDigitizer"
ix_, iy_ = 0, 0
params_: T.Dict[str, T.Any] = {}
args_ = None

# NOTE: remember these are cv2 coordinates and not numpy.
coords_: T.List[T.List[float]] = []
points_: T.List[T.List[float]] = []
img_ = None


def cache() -> Path:
    c = Path(tempfile.gettempdir()) / "plotdigitizer"
    c.mkdir(parents=True, exist_ok=True)
    return c


def data_to_hash(data) -> str:
    return hashlib.sha1(data).hexdigest()


def save_img_in_cache(img: np.array, filename: str = ""):
    if not filename:
        filename = f"{data_to_hash(img)}.png"
    outpath = cache() / filename
    cv2.imwrite(str(outpath), img)
    logger.debug(f" Saved to {outpath}")


def _find_center(vec):
    return np.median(vec)


def plot_traj(traj, outfile: Path):
    global coords_
    import matplotlib.pyplot as plt

    x, y = zip(*traj)
    plt.figure()
    plt.subplot(211)

    # there are numpy coords.
    for c in coords_:
        p = list(map(int, c))
        p[1] = img_.shape[0] - p[1]
        csize = img_.shape[0] // 40
        cv2.circle(img_, tuple(p), csize, 128, -1)
    plt.imshow(img_, interpolation="none", cmap="gray")
    plt.axis(False)
    plt.title("Original")
    plt.subplot(212)
    plt.title("Reconstructed")
    plt.plot(x, y)
    plt.tight_layout()
    if not str(outfile):
        plt.show()
    else:
        plt.savefig(outfile)
        logger.info(f"Saved to {outfile}")
    plt.close()


def click_points(event, x, y, flags, params):
    global img_
    assert img_ is not None, "No data set"
    # Function to record the clicks.
    if event == cv2.EVENT_LBUTTONDOWN:
        logger.info("MOUSE clicked on %s,%s" % (x, y))
        coords_.append((x, y))


def show_frame(img, msg="MSG: "):
    global WindowName_
    msgImg = np.zeros(shape=(50, img.shape[1]))
    cv2.putText(msgImg, msg, (1, 40), 0, 0.5, 255)
    newImg = np.vstack((img, msgImg.astype(np.uint8)))
    cv2.imshow(WindowName_, newImg)


def ask_user_to_locate_points(points, img):
    global coords_
    cv2.namedWindow(WindowName_)
    cv2.setMouseCallback(WindowName_, click_points)
    while len(coords_) < len(points):
        i = len(coords_)
        p = points[i]
        pLeft = len(points) - len(coords_)
        show_frame(img, "Please click on %s (%d left)" % (p, pLeft))
        if len(coords_) == len(points):
            break
        key = cv2.waitKey(1) & 0xFF
        if key == "q":
            break
    logger.info("You clicked %s" % coords_)


def list_to_points(points) -> T.List[T.List[float]]:
    ps = [[float(a) for a in x.split(",")] for x in points]
    return ps


def compute_scaling_offset(p, P):
    # Currently only linear maps and only 2D.
    px, py = zip(*p)
    Px, Py = zip(*P)
    sX, offX = np.polyfit(px, Px, 1)
    sY, offY = np.polyfit(py, Py, 1)
    return ((sX, sY), (offX, offY))


def transform_axis(img, erase_near_axis: int = 1):
    # extra: extra rows and cols to erase. Help in containing error near axis.
    # compute the transformation between old and new axis.
    T = compute_scaling_offset(points_, coords_)
    r, c = img.shape
    # x-axis and y-axis chopping can be computed by offset.
    offX, offY = T[1]
    offCols, offRows = int(round(offX)), int(round(offY))
    img[r - offRows - erase_near_axis :, :] = params_["background"]
    img[:, : offCols + erase_near_axis] = params_["background"]
    return T


def find_trajectory(img, pixel, T, error=0):
    logger.info(f"Extracting trajectory for color {pixel}")
    res = []
    r, c = img.shape
    new = np.zeros_like(img)

    # Find all pixels which belongs to a trajectory.
    o = 6
    Y, X = np.where((img > pixel - o // 2) & (img < pixel + o // 2))
    traj = defaultdict(list)
    for x, y in zip(X, Y):
        traj[x].append(y)

    (sX, sY), (offX, offY) = T
    for k in sorted(traj):
        x = k

        vals = np.array(traj[k])

        # For each x, we may multiple pixels in column of the image which might
        # be y. Usually experience is that the trajectories are close to the
        # top rather to the bottom. So we discard call pixel which are below
        # the center of mass (median here)
        # These are opencv pixles. So there valus starts from the top. 0
        # belogs to top row. Therefore > rather than <.
        avg = np.median(vals)
        vals = vals[np.where(vals >= avg)]
        if len(vals) == 0:
            continue

        # Still we have multiple candidates for y for each x.
        # We find the center of these points and call it the y for given x.
        y = _find_center(vals)
        cv2.circle(new, (x, int(y)), 2, 255, -1)
        x1 = (x - offX) / sX
        y1 = (r - y - offY) / sY
        res.append((x1, y1))

    # sort by x-axis.
    res = sorted(res)
    return res, np.vstack((img, new))


def _find_trajectory_colors(img, plot: bool = False) -> T.Tuple[int, T.List[int]]:
    # Each trajectory color x is bounded in the range x-3 to x+2 (interval of
    # 5) -> total 51 bins. Also it is very unlikely that colors which are too
    # close to each other are part of different trajecotries. It is safe to
    # assme a binwidth of at least 10px.
    hs, bs = np.histogram(img.ravel(), 255 // 10, [0, img.max()])

    # Now a trajectory is only trajectory if number of pixels close to the
    # width of the image (we are using at least 75% of width).
    hs[hs < img.shape[1] * 3 // 4] = 0

    if plot:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.bar(bs[:-1], np.log(hs))
        plt.xlabel("color")
        plt.ylabel("log(#pixel)")
        plt.show()

    # background is usually the color which is most count. We can find it
    # easily by sorting the histogram.
    hist = sorted(zip(hs, bs), reverse=True)

    # background is the most occuring pixel value.
    bgcolor = int(hist[0][1])

    # we assume that bgcolor is close to white.
    if bgcolor < 128:
        logger.error(
            "I computed that background is 'dark'. I don't work with images "
            "with dark background. Even if this was a mistake, I've failed."
        )
        quit(-1)

    # foreground are peaks which are away from foreground. If background is
    # white, search from the trajectories from the black.
    trajcolors = [int(b) for h, b in hist if h > 0 and b / bgcolor < 0.5]
    return bgcolor, trajcolors


def compute_foregrond_background_stats(img) -> T.Dict[str, T.Any]:
    """Compute foreground and background color."""
    params: T.Dict[str, T.Any] = {}
    # Compute the histogram. It should be a multimodal histogram. Find peaks
    # and these are the colors of background and foregorunds. Currently
    # implementation is very simple.
    bgcolor, trajcolors = _find_trajectory_colors(img)
    params["background"] = bgcolor
    params["timeseries_colors"] = trajcolors
    logger.debug(f" computed parameters: {params}")
    return params


def process(img):
    global params_
    global args_
    params_ = compute_foregrond_background_stats(img)
    T = transform_axis(img, erase_near_axis=1)

    # extract the plot that has color which is farthest from the background.
    trajcolor = params_["timeseries_colors"][0]
    traj, img = find_trajectory(img, trajcolor, T)
    save_img_in_cache(img, f"{args_.INPUT.name}.final.png")
    return traj


def run(args):
    global coords_, points_
    global img_, args_
    args_ = args
    if args_.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    infile = Path(args.INPUT)
    assert infile.exists(), f"{infile} does not exists."
    logger.info("Got file: %s" % infile)

    img_ = cv2.imread(str(infile), 0)
    img_ = img_ - img_.min()
    img_ = (255 * (img_ / img_.max())).astype(np.uint8)

    assert img_.max() <= 255
    assert img_.min() < img_.mean() < img_.max(), "Could not read meaningful data"

    save_img_in_cache(img_, args_.INPUT.name)

    points_ = list_to_points(args.data_point)
    coords_ = list_to_points(args.location)

    if len(coords_) != len(points_):
        logger.debug(
            "Either location is not specified or their numbers don't"
            " match with given datapoints. Asking user..."
        )
        ask_user_to_locate_points(points_, img_)

    # opencv has (0,0) on top-left while numpy has at bottom left. Converting
    # opencv axis to numpy axis.
    yoffset = img_.shape[0]
    coords_ = [(x, yoffset - y) for (x, y) in coords_]
    logger.info(f" translated to numpy-axis {coords_}")

    # erosion after dilation (closes gaps)
    if args_.preprocess:
        kernel = np.ones((1, 1), np.uint8)
        img_ = cv2.morphologyEx(img_, cv2.MORPH_CLOSE, kernel)
        save_img_in_cache(img_, f"{args_.INPUT.name}.close.png")

    traj = process(img_)

    if args_.plot is not None:
        plot_traj(traj, args_.plot)

    outfile = args.output or "%s.traj.csv" % args.INPUT
    with open(outfile, "w") as f:
        for r in traj:
            f.write("%g %g\n" % (r))
    logger.info("Wrote trajectory to %s" % outfile)


def main():
    # Argument parser.
    import argparse

    description = """Digitize image."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("INPUT", type=Path, help="Input image file.")
    parser.add_argument(
        "--data-point",
        "-p",
        required=True,
        action="append",
        help="Datapoints (min 3 required). You have to click on them later."
        " At least 3 points are recommended. e.g -p 0,0 -p 10,0 -p 0,1 "
        "Make sure that point are comma separated without any space.",
    )
    parser.add_argument(
        "--location",
        "-l",
        required=False,
        default=[],
        action="append",
        help="Location of a points on figure in pixels (integer)."
        " These values should appear in the same order as -p option."
        " If not given, you will be asked to click on the figure.",
    )
    parser.add_argument(
        "--plot",
        default=None,
        required=False,
        help="Plot the final result. Requires matplotlib.",
    )

    parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=str,
        help="Name of the output file else trajectory will be written to "
        " <INPUT>.traj.csv",
    )
    parser.add_argument(
        "--preprocess",
        required=False,
        action="store_true",
        help="Preprocess the image. Useful with bad resolution images.",
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        help="Enable debug logger",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
