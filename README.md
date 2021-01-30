![Python application](https://github.com/dilawar/PlotDigitizer/workflows/Python%20application/badge.svg) [![PyPI version](https://badge.fury.io/py/plotdigitizer.svg)](https://badge.fury.io/py/plotdigitizer) [![DOI](https://zenodo.org/badge/140683649.svg)](https://zenodo.org/badge/latestdoi/140683649)

A Python3 utility to digitize plots. 

## Installation

```
$ python3 -m pip install plotdigitizer 
$ plotdigitizer --help
```

## Usage

First, remove all text from the image, leave only axis and the plot. I use
`gthumb` utility. You can also use imagemagick or gimp.

Following image is from MacFadden and Koshland, PNAS 1990 after trimming. One
can also remove top and right axis.

![Trimmed image](./figures/trimmed.png)

__Run the utility__

```
plotdigitizer ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

We need three points (`-p` option) to map axes onto the images.  In the example
above, these are `0,0` (where x-axis and y-axis intesect) , `20,0` (a point on
x-axis) and `0,1` (a point on y-axis). To map these points on the image, you
will be asked to click on these points on the image. _Make sure to click in
the same order and click on the points as precisely as you could. Any error in
this step will propagate._

The data-points will be dumped to a csv file e.g., __`--output
/path/to/file.csv`__. 

If `--plot output.png` is passed, a plot of the extracted data-points will be
saved to `output.png`. This requires `matplotlib`.

![](./figures/traj.png)

Notice the errors near the boxes; since we have not trimmed them.

### Using in batch mode

You can also pass the location of points in the image at the command prompt.
This allows it to run in the batch mode without any need for the user to click
on the image.

```bash
plotdigitizer ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 -l 22,295 -l 142,295 -l 22,215 --plot output.png
```


# Examples

![original](./figures/graphs_1.png)

```bash
plotdigitizer figures/graphs_1.png \
		-p 1,0 -p 6,0 -p 0,3 \
		-l 165,160 -l 599,160 -l 85,60 \
		--plot figures/graphs_1.result.png \
		--preprocess
```

![reconstructed](./figures/graphs_1.result.png)


![original](./figures/ECGImage.png)

```
plotdigitizer  figures/ECGImage.png \
		-p 1,0 -p 5,0 -p 0,1 -l 290,337 \
		-l 1306,338 -l 106,83 \
		--plot figures/ECGImage.result.png
```

![reconstructed](./figures/ECGImage.result.png)

# Limitations

Currently this script has following limitations:

- Background must not be transparent. It might work with transparent background but
  I've not tested it.
- Only b/w images are supported for now. Color images will be converted to grayscale upon reading.
- One image should have only one trajectory.

## Related projects by others

1.  [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit
Rohatagi is very versatile.
