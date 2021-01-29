[![Build Status](https://travis-ci.org/dilawar/PlotDigitizer.svg?branch=master)](https://travis-ci.org/dilawar/PlotDigitizer) [![PyPI version](https://badge.fury.io/py/PlotDigitizer.svg)](https://badge.fury.io/py/PlotDigitizer) 

# PlotDigitizer

A python (python3) script to digitize plot (Under developement)

## Usage

1. Remove all the text from the image. Only axis and plot should be left.

For example, following image is from MacFadden and Koshland, PNAS 1990. 
![](./figures/original.png)

It should be trimmed. Remove the top border. You can use `gimp`
or `imagemagick` or `gthumb` or any other tool for cropping.

![](./figures/trimmed.png)

2. Then we run the script like this.

```
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

Option `-i` accepts the input file. 

We need three `-p` (points) to map the coordinates onto the pixels of the
image. In the example above, we have given three coordinates: `0,0` (where
x-axis and y-axis intesect) , `20,0` (a point on x-axis) and `0,1` (a point on
y-axis). To map thse points on the pixels, we are going to click on the image
to locate these coordinates later. __Make sure to click in the same order.__

3. The data-points will be dumped to a csv file. If `--plot output.png` is
passed, it will also plot the computed data-points to `output.png`. This
requires `matplotlib`.

![](./figures/traj.png)

Notice the errors near the boxes; since we have not trimmed them.

### Passing the location of coordinates manually

__IMP/FIXME:__ Bottom left corner of the image is `(0,0)` in most plots. However, for
opencv which we are using in this project, top-left is mapped to `(0,0)`. This
may cause subtle effects if you are not careful when passing values of location
manually.  See issue #1 for discussion. I got these values from program `gimp`.

```bash
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
    -l 22,295 -l 142,295 -l 22,215 --plot output.png
```

## Dependencies

Install Python bindings of `opencv` manually. On ubuntu box, it is available in
official repositories ie., `$ sudo apt install python3-opencv`. You can also
use the Python wheel available here https://pypi.org/project/opencv-python/
e.g. `$ pip install opencv-python --user`.

## Limitations

Currently this script has following limitations:

- Background must not be transparent. It might work with transparent background but
  I've not tested it.
- Only b/w images are supported for now. Color images will be converted to grayscale upon reading.
- One image should have only one trajectory.

You might be interested in more versatile
[WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit Rohatagi.

# Development

If you enhance the script, feel free to send a PR.
