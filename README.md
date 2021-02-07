![Python application](https://github.com/dilawar/PlotDigitizer/workflows/Python%20application/badge.svg) [![PyPI version](https://badge.fury.io/py/plotdigitizer.svg)](https://badge.fury.io/py/plotdigitizer) [![DOI](https://zenodo.org/badge/140683649.svg)](https://zenodo.org/badge/latestdoi/140683649)

A Python3 utility to digitize plots. 

This utility is meant for use cases where similar plots needs to be digitized in batch mode; such as EEG,
ECG recordings.

Feel free to contact for commercial work that may require optimizing this pipeline 
for your use case. Please send a sample plot.

For one time use case, you may prefer [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit
Rohatagi which is very user friendly.

## Installation

```
$ python3 -m pip install plotdigitizer 
$ plotdigitizer --help
```

## Preparing image

Crop the image such that most of the text (if any) is removed. I use
`gthumb` utility. You can also use imagemagick or gimp.

Following image is from MacFadden and Koshland, PNAS 1990 after trimming. One
can also remove top and right axis.

![Trimmed image](./figures/trimmed.png)

__Run the utility__

```
plotdigitizer ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

We need at least three points (`-p` option) to map axes onto the images.  In the example
above, these are `0,0` (where x-axis and y-axis intesect) , `20,0` (a point on
x-axis) and `0,1` (a point on y-axis). To map these points on the image, you
will be asked to click on these points on the image. _Make sure to click in
the same order and click on the points as precisely as you could. Any error in
this step will propagate._ If you don't have `0,0` in your image, you have to provide 
4 points: 2 on x-axis and 2 on y-axis.

The data-points will be dumped to a csv file specified by __`--output
/path/to/file.csv`__. 

If `--plot output.png` is passed, a plot of the extracted data-points will be
saved to `output.png`. This requires `matplotlib`.

![](./figures/traj.png)

Notice the errors near the boxes; since we have not trimmed them.

## Using in batch mode

You can pass the coordinates of points in the image at the command prompt.
This allows to run in the batch mode without any need for the user to click on
the image.

```bash
plotdigitizer ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 -l 22,295 -l 142,295 -l 22,215 --plot output.png
```

### How to find coordinates of axes points

In the example above, point `0,0` is mapped to coordinate `22,295` i.e., the
data point `0,0` is on the 22nd row and 295th column of the image (_assuming that bottom left
of the image is first row, first column `(0,0)`_). I have included an utility
`plotdigitizer-locate` (script `plotdigitizer/locate.py`) which you can use to
find the coordinates.

If you have installed the utility using `pip install`

```bash
$ plotdigitizer-locate figures/trimmed.png     
```

or, from the source,

```bash
$ python3 plotdigitizer/locate.py figures/trimmed.png
```

This command will open a window, you can now click on the desired point. Its coordinate will
be written on the image itself. Note them down.

![](./figures/trimmed_locate.png)


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

## Need help

Open an issue and please attach the sample plot.

## Related projects by others

1.  [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit
Rohatagi is very versatile.
