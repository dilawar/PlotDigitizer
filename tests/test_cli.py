__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import sys
import subprocess
import numpy as np
from pathlib import Path

import plotdigitizer

HERE = Path(__file__).parent.resolve()


def _run_cmdline(infile: Path, points, locations):
    cmd = f"plotdigitizer {str(infile)} "
    pts = " ".join([f"-p {','.join(map(str,pt))}" for pt in points])
    locs = " ".join([f"-l {','.join(map(str,pt))}" for pt in locations])
    cmd += f"{pts} {locs}"
    outfile = infile.with_suffix(".result.png")
    trajfile = infile.with_suffix(".result.csv")
    cmd += f" --plot {str(outfile)} --output {trajfile}"
    r = subprocess.run(cmd, check=True, shell=True)
    assert r.returncode == 0, f"Failed test {r.returncode}"
    return trajfile


def _check_csv_file(csvfile):
    data = np.loadtxt(csvfile)
    y = data[:, 1]
    assert y.std() > 0.0
    assert y.min() < y.mean() < y.max()


def test_trimmeed():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "trimmed.png",
        [(0, 0), (20, 0), (0, 1)],
        [(22, 26), (142, 23), (23, 106)],
    )
    _check_csv_file(csvfile)


def test_graph1():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graphs_1.png",
        [(1, 0), (6, 0), (0, 3)],
        [(165, 52), (599, 51), (85, 151)],
    )
    _check_csv_file(csvfile)


def test_ecg():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "ECGImage.png",
        [(1, 0), (5, 0), (0, 1)],
        [(290, 44), (1306, 43), (106, 301)],
    )
    _check_csv_file(csvfile)


def test_grid():
    csvfile = _run_cmdline(
        HERE / ".." / "figures" / "graph_with_grid.png",
        [(200, 0), (1000, 0), (0, 50)],
        [(269, 69), (1780, 69), (81, 542)],
    )
    _check_csv_file(csvfile)
