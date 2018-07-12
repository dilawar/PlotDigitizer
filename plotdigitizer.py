#!/usr/bin/env python3
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import logging
import math

import logging
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    )

windowName_ = "PlotDigitizer" 
cv2.namedWindow( windowName_ )
ix_, iy_ = 0, 0

# NOTE: remember these are cv2 coordinates and not numpy.
coords_ = []

points_ = []
mapping_ = {}
img_    = None

def click_points( event, x, y, flags, params ):
    global img_
    assert img_ is not None, "No data set"
    # Function to record the clicks.
    r, c = img_.shape
    if event == cv2.EVENT_LBUTTONDOWN:
        y = r - y
        logging.info( "MOUSE clicked on %s,%s" % (x,y))
        coords_.append( (x, y) )

cv2.setMouseCallback( windowName_, click_points )

def show_frame( img, msg = 'MSG: ' ):
    global windowName_
    cv2.imshow( windowName_, img )

def ask_user_to_locate_points(  points, img ):
    global coords_
    while len(coords_) < len(points):
        i = len(coords_)
        p = points[i]
        pLeft = len(points) - len(coords_)
        show_frame( img, 'Please click on %s (%d left)' % (p, pLeft) )
        if len(coords_) == len(points):
            break
        key = cv2.waitKey(1) & 0xFF
        if key == 'q':
            break

    logging.info( "You clicked %s" % coords_ )

def list_to_points( points ):
    ps = [ [ float(a) for a in x.split(',')] for x in points]
    return ps

def compute_scaling_offset( p, P ):
    # Currently only linear maps and only 2D. 
    px, py = zip(*p)
    Px, Py = zip(*P)
    sX, offX = np.polyfit( px, Px, 1 )
    sY, offY = np.polyfit( py, Py, 1 )
    return ((sX,sY), (offX, offY))

def filter_plot( img ):
    # Following filters are applied.
    # - Open followed by close 
    # - No smoothing etc. They destroy the data plots.
    hist, bins = np.histogram( img.ravel(), 256, [0, 256], normed = True )
    print( hist )

def extract_trajectories( img ):
    # First some filtering.
    img = filter_plot( img )

def chop_axis( img ):
    global mapping_

    # compute the transformation between old and new axis.
    T = compute_scaling_offset( points_, coords_ )
    r, c = img.shape
    # x-axis and y-axis chopping can be computed by offset.
    offX, offY = T[1]
    offCols, offRows = int(round(offX)), int(round(offY))
    imgAtOrigin = img[:r-offRows, offCols:]
    cv2.imwrite( 'imgwithoutaxis.png', imgAtOrigin )
    traj = extract_trajectories( imgAtOrigin )
    print( traj )


def process( img ):
    img = chop_axis( img )


def main( args ):
    global coords_, points_
    global img_
    infile = args.input
    logging.info( 'Processing %s' % infile )
    img_ = cv2.imread( infile, 0 )
    cv2.imwrite( 'original.png', img_ )
    points_ = list_to_points( args.point )
    coords_ = list_to_points( args.location )
    if len(coords_) != len(points_):
        ask_user_to_locate_points(points_, img_)
    process( img_ )

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''Digitize image.'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input', '-i'
        , required = True
        , help = 'Input image file.'
        )
    parser.add_argument('--type', '-t'
        , required = False, default = 'line'
        , help = 'Type of image (xy line)'
        )
    parser.add_argument('--num-axis', '-n'
        , required = False, default = 2
        , help = 'Number of axis (currently only 2 axis are supported)'
        )
    parser.add_argument('--point', '-p'
        , required = True
        , action = 'append'
        , help = 'Please specify a datapoint. You have to manually click them on '
                ' the figure. At least 2 points are required. 3 are recommended. e.g. '
                '   -p 0,0 -p 1,0 -p 0,1 '
                'Make sure that point are comma separated without any space e.g.'
                ' -p 0, 1 is wrong.'
        )
    parser.add_argument('--location', '-l'
        , required = False, default = []
        , action = 'append'
        , help = 'Location of a given point on figure in pixels (integer).'
                 ' These values should appear in the same order as -p option.'
                 ' If not given, you will be asked to click on the figure.'
        )
    class Args: pass 
    args = Args()
    parser.parse_args(namespace=args)
    main( args )
