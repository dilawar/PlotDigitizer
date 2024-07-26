# image functions.


from pathlib import Path
import typing as T
from loguru import logger

import cv2 as cv
import numpy as np
import numpy.typing as npt

from plotdigitizer import common
from plotdigitizer import geometry
from plotdigitizer import grid
from plotdigitizer import plot
from plotdigitizer.trajectory import find_trajectory


def click_points(event, x, y, _flags, params):
    """callback for opencv image"""
    assert common.img_ is not None, "No data set"
    # Function to record the clicks.
    YROWS = common.img_.shape[0]
    if event == cv.EVENT_LBUTTONDOWN:
        logger.info(f"You clicked on {(x, YROWS-y)}")
        common.locations_.append(geometry.Point(x, YROWS - y))


class Figure:
    def __init__(self, path: Path, coordinates: T.List[str], indices: T.List[str]):
        assert path.exists(), f"{path} does not exists."
        logger.info(f"Reading {path}")
        self.indices = list_to_points(indices)
        self.coordinates = list_to_points(coordinates)
        self.path = path
        self.orignal = cv.imread(self.path)
        self.imgs = [("orig-gray-normalized", normalize(cv.imread(self.path, 0)))]

    def remove_grid(self):
        self._append("remove-grid", grid.remove_grid(self._last()))
        save_img_in_cache(self._last(), Path(f"{self.path.name}.without_grid.png"))
        self._append("normalize", normalize(self._last()))
        img = self._last()
        logger.debug(f" {img.min()=} {img.max()=}")
        assert img.max() <= 255
        assert img.min() < img.mean() < img.max(), "Could not read meaningful data"

    def trajectories(self):
        return process_image(self._last(), "_image")

    def extract_trajectories(self):
        logger.info(f"Extracting trajectories from {infile}")

    def map_axis(self):
        logger.info("Mapping axis...")
        logger.debug(
            f"data points {self.coordinates} → location on image {self.indices}"
        )

        if len(self.coordinates) != len(self.indices):
            logger.warning(
                "Either the location of data-points on the image is not specified or their numbers don't"
                " match with given datapoints. Asking user to fill the missing information..."
            )

            # next function uses callback. Needs a global variable to collect
            # data.
            common.locations_ = self.indices
            self.indices = ask_user_to_locate_points(self.coordinates, self._last())
        assert len(self.coordinates) == len(self.indices)

    def _last(self):
        return self.imgs[-1][1]

    def _append(self, operation: str, img):
        self.imgs.append((operation, img))


def process_image(img, cache_key: T.Optional[str] = None):
    global params_
    common.params_ = compute_foregrond_background_stats(img)

    T = transform_axis(img, erase_near_axis=3)
    assert img.std() > 0.0, "No data in the image!"
    logger.info(f" {img.mean()}  {img.std()}")
    if cache_key is not None:
        save_img_in_cache(img, f"{cache_key}.transformed_axis.png")

    # extract the plot that has color which is farthest from the background.
    trajcolor = common.params_["timeseries_colors"][0]
    img = normalize(img)
    traj, img = find_trajectory(img, trajcolor, T)
    if cache_key is not None:
        save_img_in_cache(img, f"{cache_key}.final.png")
    return traj


def compute_foregrond_background_stats(img) -> T.Dict[str, T.Any]:
    """Compute foreground and background color."""
    params: T.Dict[str, T.Any] = {}
    # Compute the histogram. It should be a multimodal histogram. Find peaks
    # and these are the colors of background and foregorunds. Currently
    # implementation is very simple.
    bgcolor, trajcolors = find_trajectory_colors(img)
    params["background"] = bgcolor
    params["timeseries_colors"] = trajcolors
    logger.debug(f" computed parameters: {params}")
    return params


def find_trajectory_colors(
    img: np.ndarray, plot: bool = False
) -> T.Tuple[int, T.List[int]]:
    # Each trajectory color x is bounded in the range x-3 to x+2 (interval of
    # 5) -> total 51 bins. Also it is very unlikely that colors which are too
    # close to each other are part of different trajecotries. It is safe to
    # assme a binwidth of at least 10px.
    hs, bs = np.histogram(img.flatten(), 255 // 10, (0, img.max()))

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


def axis_transformation(p, P: T.List[geometry.Point]):
    """Compute m and offset for model Y = m X + offset that is used to transform
    axis X to Y"""

    # Currently only linear maps and only 2D.
    px, py = zip(*p)
    Px, Py = zip(*P)
    offX, sX = np.polyfit(px, Px, 1)
    offY, sY = np.polyfit(py, Py, 1)
    return ((sX, sY), (offX, offY))


def transform_axis(img, erase_near_axis: int = 0):
    global locations_
    global points_
    # extra: extra rows and cols to erase. Help in containing error near axis.
    # compute the transformation between old and new axis.
    T = axis_transformation(common.points_, common.locations_)
    p = geometry.find_origin(common.locations_)
    offCols, offRows = p.x, p.y
    logger.info(f"{common.locations_} → origin {offCols}, {offRows}")
    img[:, : offCols + erase_near_axis] = common.params_["background"]
    img[-offRows - erase_near_axis :, :] = common.params_["background"]
    logger.debug(f"Tranformation params: {T}")
    return T


def save_img_in_cache(
    img: npt.ArrayLike, filename: T.Optional[T.Union[Path, str]] = None
):
    if filename is None:
        filename = Path(f"{common.data_to_hash(img)}.png")
    outpath = common.cache() / filename
    cv.imwrite(str(outpath), np.array(img))
    logger.debug(f" Saved to {outpath}")


# Thanks https://codereview.stackexchange.com/a/185794
def normalize(img):
    """normalize image to 0, 255"""
    return np.interp(img, (img.min(), img.max()), (0, 255)).astype(np.uint8)


def list_to_points(points) -> T.List[geometry.Point]:
    ps = [geometry.Point.fromCSV(x) for x in points]
    return ps


def ask_user_to_locate_points(points, img) -> list:
    """Ask user to map axis. Callback function save selected points in
    common.locations_"""
    cv.namedWindow(common.WindowName_)
    cv.setMouseCallback(common.WindowName_, click_points)
    while len(common.locations_) < len(points):
        i = len(common.locations_)
        p = points[i]
        pLeft = len(points) - len(common.locations_)
        plot.show_frame(img, "Please click on %s (%d left)" % (p, pLeft))
        if len(common.locations_) == len(points):
            break
        key = cv.waitKey(1) & 0xFF
        if key == "q":
            break
    logger.info("You clicked %s" % common.locations_)
    return common.locations_
