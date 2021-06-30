__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2017-, Dilawar Singh"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"
__status__ = "Development"

import typing as T
from collections import defaultdict
import tempfile
import hashlib
from pathlib import Path

import cv2 as cv
import numpy as np
import numpy.polynomial.polynomial as poly

import plotdigitizer.grid as grid
import plotdigitizer.trajectory as trajectory

# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

from loguru import logger

logger.add(
    Path(tempfile.gettempdir()) / "plotdigitizer.log", level="DEBUG", rotation="10MB"
)

WindowName_ = "PlotDigitizer"
ix_, iy_ = 0, 0
params_: T.Dict[str, T.Any] = {}
args_ = None

# NOTE: remember these are cv coordinates and not numpy.
coords_: T.List[T.List[float]] = []
points_: T.List[T.List[float]] = []

img_: np.ndarray = np.zeros((1, 1))


def cache() -> Path:
    c = Path(tempfile.gettempdir()) / "plotdigitizer"
    c.mkdir(parents=True, exist_ok=True)
    return c


def data_to_hash(data) -> str:
    return hashlib.sha1(data).hexdigest()


def save_img_in_cache(img: np.ndarray, filename: T.Optional[Path] = None):
    if filename is None:
        filename = Path(f"{data_to_hash(img)}.png")
    outpath = cache() / filename
    cv.imwrite(str(outpath), img)
    logger.debug(f" Saved to {outpath}")


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
        cv.circle(img_, tuple(p), csize, 128, -1)
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
    if event == cv.EVENT_LBUTTONDOWN:
        logger.info("MOUSE clicked on %s,%s" % (x, y))
        coords_.append((x, y))


def show_frame(img, msg="MSG: "):
    global WindowName_
    msgImg = np.zeros(shape=(50, img.shape[1]))
    cv.putText(msgImg, msg, (1, 40), 0, 0.5, 255)
    newImg = np.vstack((img, msgImg.astype(np.uint8)))
    cv.imshow(WindowName_, newImg)


def ask_user_to_locate_points(points, img):
    global coords_
    cv.namedWindow(WindowName_)
    cv.setMouseCallback(WindowName_, click_points)
    while len(coords_) < len(points):
        i = len(coords_)
        p = points[i]
        pLeft = len(points) - len(coords_)
        show_frame(img, "Please click on %s (%d left)" % (p, pLeft))
        if len(coords_) == len(points):
            break
        key = cv.waitKey(1) & 0xFF
        if key == "q":
            break
    logger.info("You clicked %s" % coords_)


def list_to_points(points) -> T.List[T.List[float]]:
    ps = [[float(a) for a in x.split(",")] for x in points]
    return ps


def compute_scaling_offset(p, P) -> T.List[T.Tuple[float, float]]:
    # Currently only linear maps and only 2D.
    px, py = zip(*p)
    Px, Py = zip(*P)
    offX, sX = poly.polyfit(px, Px, 1)
    offY, sY = poly.polyfit(py, Py, 1)
    logger.info(
        f"{px=} -> {Px=}, {py=} -> {Py=} | {sX=:.2f} {offX=:.2f}, {sY=:.2f} {offY=:.2f}"
    )
    return [(sX, sY), (offX, offY)]


def transform_axis(img, erase_near_axis: int = 1):
    # extra: extra rows and cols to erase. Help in containing error near axis.
    # compute the transformation between old and new axis.
    T = compute_scaling_offset(points_, coords_)

    # FIXME: This is broken becuase compute_scaling_offset is not the right way
    # to trim the axis. Correct way to to figure out the location of axis and
    # trim from there. Can we make sure that user always click on lower side of
    # axis so I can trim below that?
    ## x-axis and y-axis chopping can be computed by offset.
    ##r, _ = img.shape
    ##offX, offY = T[1]
    ##offCols, offRows = int(round(offX)), int(round(offY))
    ##logger.info(f"Offsets: {offCols=}, {offRows=}")
    ##img[r - offRows - erase_near_axis :, :] = params_["background"]
    ##img[:, : offCols + erase_near_axis] = params_["background"]
    ##logger.info(f"erase near axis: : {erase_near_axis}")
    logger.debug(f"Tranformation params: {T}")
    return T


def _valid_px(val: int) -> int:
    return min(max(0, val), 255)


def find_trajectory(img, pixel, T):
    logger.info(f"Extracting trajectory for color {pixel}")

    # Find all pixels which belongs to a trajectory.
    o = 6
    _clower, _cupper = _valid_px(pixel - o // 2), _valid_px(pixel + o // 2)
    logger.info(f"{_clower=} {_cupper=}")

    logger.info(f"{img.min()=}, {img.max()=}")

    Y, X = np.where((img >= _clower) & (img <= _cupper))
    traj = defaultdict(list)
    for x, y in zip(X, Y):
        traj[x].append(y)

    assert traj, "Empty trajectory"

    # this is a simple fit using median.
    new = np.zeros_like(img)
    res = trajectory.fit_trajectory_using_median(traj, T, new)
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
            "I computed that background is 'dark' which is unacceptable to me."
        )
        quit(-1)

    # If the background is white, search from the trajectories from the black.
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
    logger.info(f" computed parameters: {params}")
    return params


def process_image(img):
    global params_
    global args_
    params_ = compute_foregrond_background_stats(img)

    T = transform_axis(img, erase_near_axis=1)
    save_img_in_cache(img, f"{args_.INPUT.name}.transformed_axis.png")

    # extract the plot that has color which is farthest from the background.
    trajcolor = params_["timeseries_colors"][0]
    traj, img = find_trajectory(img, trajcolor, T)
    save_img_in_cache(img, f"{args_.INPUT.name}.final.png")
    return traj


def run(args):
    global coords_, points_
    global img_, args_
    args_ = args

    infile = Path(args.INPUT)
    assert infile.exists(), f"{infile} does not exists."
    logger.info(f"Extracting trajectories from {infile}")

    img_ = cv.imread(str(infile), 0)

    # rescale.
    img_ = img_ - img_.min()
    img_ = (255 * (img_ / img_.max())).astype(np.uint8)

    assert img_.max() <= 255
    assert img_.min() < img_.mean() < img_.max(), "Could not read meaningful data"

    save_img_in_cache(img_, args_.INPUT.name)

    points_ = list_to_points(args.data_point)
    coords_ = list_to_points(args.location)
    logger.debug(f"{args.data_point=} → {args.location=}")

    if len(coords_) != len(points_):
        logger.warning(
            "Either the location of data-points are not specified or their numbers don't"
            " match with given datapoints. Asking user..."
        )
        ask_user_to_locate_points(points_, img_)

    # opencv has (0,0) on top-left while numpy has at bottom left. Converting
    # opencv axis to numpy axis.
    yoffset = img_.shape[0]
    coords_ = [(x, yoffset - y) for (x, y) in coords_]
    logger.debug(f" translated to numpy-axis {coords_}")

    # erosion after dilation (closes gaps)
    if args_.preprocess:

        kernel = np.ones((1, 1), np.uint8)
        img_ = cv.morphologyEx(img_, cv.MORPH_CLOSE, kernel)
        save_img_in_cache(img_, f"{args_.INPUT.name}.close.png")

    if args.has_grid:
        img_ = grid.remove_grid(img_)
        save_img_in_cache(img_, f"{args_.INPUT.name}.without_grid.png")

    traj = process_image(img_)

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
    parser.add_argument(
        "--has-grid",
        required=False,
        action="store_true",
        help="My images has grid which is very prominent. When this option is"
        " set, I'll try to remove the grid.",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
