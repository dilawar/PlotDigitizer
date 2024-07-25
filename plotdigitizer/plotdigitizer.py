__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T
from pathlib import Path

import cv2 as cv

import numpy as np
import typer
from typing_extensions import Annotated

from plotdigitizer import grid
from plotdigitizer import image
from plotdigitizer import geometry
from plotdigitizer import common

# Logger
import logging


app = typer.Typer()


def plot_traj(traj, outfile: Path):
    global locations_
    import matplotlib.pyplot as plt

    x, y = zip(*traj)
    plt.figure()
    plt.subplot(211)

    for p in common.locations_:
        csize = common.img_.shape[0] // 40
        cv.circle(
            common.img_, (int(p.x), int(common.img_.shape[0] - p.y)), int(csize), (128, 128, 128), -1
        )

    plt.imshow(common.img_, interpolation="none", cmap="gray")
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
        logging.info(f"Saved to {outfile}")
    plt.close()


def click_points(event, x, y, _flags, params):
    global img_
    assert img_ is not None, "No data set"
    # Function to record the clicks.
    YROWS = img_.shape[0]
    if event == cv.EVENT_LBUTTONDOWN:
        logging.info(f"You clicked on {(x, YROWS-y)}")
        locations_.append(geometry.Point(x, YROWS - y))


def show_frame(img, msg="MSG: "):
    global WindowName_
    msgImg = np.zeros(shape=(50, img.shape[1]))
    cv.putText(msgImg, msg, (1, 40), 0, 0.5, 255)
    newImg = np.vstack((img, msgImg.astype(np.uint8)))
    cv.imshow(WindowName_, newImg)


def ask_user_to_locate_points(points, img):
    global locations_
    cv.namedWindow(WindowName_)
    cv.setMouseCallback(WindowName_, click_points)
    while len(locations_) < len(points):
        i = len(locations_)
        p = points[i]
        pLeft = len(points) - len(locations_)
        show_frame(img, "Please click on %s (%d left)" % (p, pLeft))
        if len(locations_) == len(points):
            break
        key = cv.waitKey(1) & 0xFF
        if key == "q":
            break
    logging.info("You clicked %s" % locations_)


def list_to_points(points) -> T.List[geometry.Point]:
    ps = [geometry.Point.fromCSV(x) for x in points]
    return ps


@app.command()
def digitize_plot(
    infile: Path,
    data_point: Annotated[
        T.List[str],
        typer.Option(
            "--data-point",
            "-p",
            help="Datapoints (min 3 required). You have to click on them later "
            "e.g. `-p 0,0 -p 10,0 -p 0,1`. Make sure that point are comma "
            "separated without any space.",
        ),
    ],
    location: Annotated[
        T.List[str],
        typer.Option(
            "--location",
            "-l",
            help="Location of a points on figure in pixels (integer)[."
            " These values should appear in the same order as -p option."
            " If not given, you will be asked to click on the figure.",
        ),
    ] = [],
    plot_file: Annotated[
        T.Optional[Path],
        typer.Option("--plot-file", help="Plot the final result. Requires matplotlib"),
    ] = None,
    output: Annotated[
        T.Optional[Path],
        typer.Option(
            "--output", "-o", help="Name of the output file (default <INPUT>.traj.csv)"
        ),
    ] = None,
    preprocess: Annotated[
        bool,
        typer.Option(
            "--preprocess",
            "-P",
            help="Preprocess the image. Useful with bad resolution images",
        ),
    ] = False,
):
    global locations_, points_
    global img_

    assert infile.exists(), f"{infile} does not exists."
    logging.info(f"Extracting trajectories from {infile}")

    # reads into gray-scale.
    common.img_ = cv.imread(str(infile), 0)
    common.img_ = image.normalize(img_)

    # erosion after dilation (closes gaps)
    if preprocess:
        kernel = np.ones((1, 1), np.uint8)
        common.img_ = cv.morphologyEx(img_, cv.MORPH_CLOSE, kernel)
        image.save_img_in_cache(img_, Path(f"{infile.name}.close.png"))

    # remove grids.
    img_ = grid.remove_grid(img_)
    image.save_img_in_cache(img_, Path(f"{infile.name}.without_grid.png"))

    # rescale it again.
    common.img_ = image.normalize(common.img_)
    logging.debug(" {common.img_.min()=} {common.img_.max()=}")
    assert common.img_.max() <= 255
    assert common.img_.min() < common.img_.mean() < common.img_.max(), "Could not read meaningful data"
    image.save_img_in_cache(common.img_, infile.name)

    common.points_ = list_to_points(data_point)
    common.locations_ = list_to_points(location)
    logging.debug(f"data points {data_point} → location on image {location}")

    if len(locations_) != len(common.points_):
        logging.warning(
            "Either the location of data-points are not specified or their numbers don't"
            " match with given datapoints. Asking user..."
        )
        ask_user_to_locate_points(common.points_, common.img_)

    traj = image.process_image(common.img_)

    if plot_file is not None:
        plot_traj(traj, plot_file)

    outfile = output or f"{infile}.traj.csv"
    with open(outfile, "w") as f:
        for r in traj:
            f.write("%g %g\n" % (r))
    logging.info("Wrote trajectory to %s" % outfile)


def main() -> T.Any:
    return app()
