[![Build Status](https://travis-ci.org/dilawar/PlotDigitizer.svg?branch=master)](https://travis-ci.org/dilawar/PlotDigitizer) [![PyPI version](https://badge.fury.io/py/PlotDigitizer.svg)](https://badge.fury.io/py/PlotDigitizer) 

A python3 script to digitize old plot. 

## Usage

### Remove all text from the image, leave only axis and the plot.

For example, following image is from MacFadden and Koshland, PNAS 1990 after
trimming. One can also remove top and right axis.

![Trimmed image](./figures/trimmed.png)

### Run the script

```
python3 plotdigitizer.py ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

We need three points (`-p` option) to map the coordinates onto the images.  In
the example above, we have given three coordinates: `0,0` (where x-axis and
y-axis intesect) , `20,0` (a point on x-axis) and `0,1` (a point on y-axis). To
map thse points on the image, you will be asked to click on these points on the
image. __Make sure to click in the same order.__

The data-points will be dumped to a csv file. If `--plot output.png` is
passed, it will also plot the computed data-points to `output.png`. This
requires `matplotlib`.

![](./figures/traj.png)

Notice the errors near the boxes; since we have not trimmed them.

### Mapping coordinates at command line (batch mode)

You can also pass the location of points on the command prompt. This feature
allows this script to run in batch mode without any need for the user to click
on the image.

```bash
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
    -l 22,295 -l 142,295 -l 22,215 --plot output.png
```

## Dependencies

Install Python bindings of `opencv` manually. On ubuntu box, it is available in
official repositories ie., `$ sudo apt install python3-opencv`. You can also
use the Python wheel available here https://pypi.org/project/opencv-python/
e.g. `python3 -m pip install opencv-python --user`.

## Limitations

Currently this script has following limitations:

- Background must not be transparent. It might work with transparent background but
  I've not tested it.
- Only b/w images are supported for now. Color images will be converted to grayscale upon reading.
- One image should have only one trajectory.

# Examples

![](./figures/graphs_1.png)

```bash
python3 ./plotdigitizer.py figures/graphs_1.png \
		-p 1,0 -p 6,0 -p 0,3 \
		-l 165,160 -l 599,160 -l 85,60 \
		--plot figures/graphs_1.result.png \
		--preprocess
```

![](./figures/graphs_1.result.png)


## Related projects by others

1.  [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit
Rohatagi is very versatile.

```

## Related projects by others

1.  [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit
Rohatagi is very versatile.
