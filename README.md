[![Build Status](https://travis-ci.org/dilawar/PlotDigitizer.svg?branch=master)](https://travis-ci.org/dilawar/PlotDigitizer) [![PyPI version](https://badge.fury.io/py/PlotDigitizer.svg)](https://badge.fury.io/py/PlotDigitizer) 

# PlotDigitizer

A python (python3) script to digitize plot (Under developement)

# Usage

1. Remove all the text from the image. Only axis and plot should be left.

This is from MacFadden and Koshland, PNAS 1990. 
![](./figures/original.png)

It should be trimmed. Ideally you should also remove the top border. You can use `gimp`
or `imagemagick` or any other tool for cropping.

![](./figures/trimmed.png)

2. Then we run the script like this.

```
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

Option `-i` accepts the input file. 

We need at least 3 of them to map the coordinate systems onto the pixel-system
in the image. These points are passed by repeated `-p` options. In the example
above, we have given three data-points `0,0` (where x-axis and y-axis intesect)
, `20,0` (a point on x-axis) and `0,1` (a point on y-axis).

We are going to click on the image to locate these coordinates later. Make sure
to click in the same order. 

3. The data-points will be dumped to a csv file. If `--plot` option is given from command 
line, it will also plot the computed data-points. This requires `matplotlib`.

![](./figures/traj.png)

Notice the errors near the boxes; since we have not trimmed them.

# Passing the location of coordinates manually

__IMP:__ Bottom left corner of the image is `(0,0)` in most plots. However, for
opencv which we are using in this project, top-left is mapped to `(0,0)`. This
may cause subtle effects if you are not careful when passing values of location
manually.  See issue #1 for discussion. I got these values from program `gimp`.

```bash
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
    -l 22,295 -l 142,295 -l 22,215 --plot
```

# Limitations

Currently this script has following limitations:

- Background must not be transparent. It might work with transparent background but
  I've not tested it.
- Only b/w images are supported for now. Color images will be converted to grayscale upon reading.
- One image should have only one trajectory.

You might be interested in more versatile
[WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit Rohatagi.

# Development

If you enhance the script, feel free to send a PR.
