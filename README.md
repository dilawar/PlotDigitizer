# PlotDigitizer

Python3 app to digitize plot (Under developement)

# Flow

1. Remove all the text from the image. Only axis and plot should be left.

![](./figures/original.png)

Should be converted to 

![](./figures/trimmed.png)

2. Then we run the script like this.

```
./plotdigitizer.py -i ./figures/trimmed.png -p 0,0 -p 10,0 -p 0,1
```

Option `-i` accepts the input file. The important bit is repeating `-d` options.
These are the data-points. We need at least 3 of them. In this example, we are
telling the script that I am going to click on 3 points on the image
respectively.  These clicks will map to those 3 data-points. Make sure to click
them in order. 

__IMP:__ Left bottom corner of the  image is `(0,0)`. 

Once you have clicked on these points, the algorithm will run and extract the
trajectory. 

Currently this script has following limitations 

- Background must not be transparent. Might work with transparent background but
  I've not tested it.
- One image should have only one trajectory.

You might be interested in more versatile
[WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) by Ankit Rohatagi.

# Development

If you enhance the script, feel free to send a PR.
