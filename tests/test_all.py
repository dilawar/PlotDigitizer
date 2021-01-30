__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import sys
import subprocess
import numpy as np
from loguru import logger
from pathlib import Path

HERE = Path(__file__).parent.resolve()


def _run_cmdline(infile: Path, points, locations):
    scriptpath = HERE / ".." / "plotdigitizer" / "plotdigitizer.py"
    cmd = f"{sys.executable} {scriptpath} {infile} "
    pts = " ".join([f"-p {','.join(map(str,pt))}" for pt in points])
    locs = " ".join([f"-l {','.join(map(str,pt))}" for pt in locations])
    cmd += f"{pts} {locs}"
    outfile = infile.with_suffix(".result.png")
    trajfile = infile.with_suffix(".result.csv")
    cmd += f" --plot {outfile} --output {trajfile}"
    cmd = [x for x in cmd.split(" ") if x.strip()]
    r = subprocess.run(cmd, check=True)
    assert r.returncode == 0, f"Failed test {r.returncode}"
    return trajfile


def _check_csv_file(csvfile):
    data = np.loadtxt(csvfile)
    y = data[:, 1]
    assert y.std() > 0.0
    assert y.min() < y.mean() < y.max()


def test_examples():
    csvfile = _run_cmdline(
        HERE / Path("../figures/trimmed.png"),
        [(0, 0), (20, 0), (0, 1)],
        [(22, 295), (142, 296), (23, 215)],
    )
    _check_csv_file(csvfile)

    csvfile = _run_cmdline(
        HERE / Path("../figures/un2.png"),
        [(0, 0), (20, 0), (0, 1)],
        [(2, 754), (897, 754), (643, 583)],
    )
    _check_csv_file(csvfile)

    csvfile = _run_cmdline(
        HERE / Path("../figures/graphs_1.png"),
        [(1, 0), (6, 0), (0, 3)],
        [(165, 160), (599, 160), (85, 60)],
    )
    _check_csv_file(csvfile)

    csvfile = _run_cmdline(
        HERE / Path("../figures/ECGImage.png"),
        [(1, 0), (5, 0), (0, 1)],
        [(290, 337), (1306, 338), (106, 83)],
    )
    _check_csv_file(csvfile)


def main():
    test_examples()


if __name__ == "__main__":
    main()
