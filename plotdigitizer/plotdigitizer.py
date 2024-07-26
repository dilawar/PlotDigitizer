__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T
from pathlib import Path

import typer
from typing_extensions import Annotated

from plotdigitizer import grid
from plotdigitizer import image
from plotdigitizer import plot
from plotdigitizer import geometry
from plotdigitizer import common

# Logger
from loguru import logger


app = typer.Typer()


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
    remove_grid: Annotated[
        bool,
        typer.Option(
            "--remove-grid",
            "-rg",
            help="Try to remove grid.",
        ),
    ] = False,
    invert_image: Annotated[
        bool,
        typer.Option(
            "--invert-image",
            "-ii",
            help="Invert image (use it when background is dark).",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Just analyze the image and dump coodinates.  Useful when developing/debugging.",
        ),
    ] = False,
):
    figure = image.Figure(infile, data_point, location)
    if invert_image:
        figure.invert_image()

    # remove grids.
    if remove_grid:
        figure.remove_grid(debug)

    # map the axis
    figure.map_axis()

    # compute trajectories
    traj = figure.trajectories()

    if plot_file is not None:
        plot.plot_traj(traj, figure._last(), plot_file)

    outfile = output or f"{infile}.traj.csv"
    with open(outfile, "w") as f:
        for r in traj:
            f.write("%g %g\n" % (r))
    logger.info("Wrote trajectory to %s" % outfile)


def main() -> T.Any:
    return app()
