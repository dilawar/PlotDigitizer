#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import numpy as np
import cv2
import logging
import math
import tempfile
import argparse
from collections import defaultdict

import logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    )

windowName_ = "PlotDigitizer" 
ix_, iy_ = 0, 0
params_  = {}
args_    = None

# NOTE: remember these are cv2 coordinates and not numpy.
coords_  = []
points_  = []
mapping_ = {}
img_     = None
debug_   = False

def temp():
    return tempfile.gettempdir()

def find_center( vec ):
    # Find mode of the vector. We do it in following way. We take the bin which
    # has most member and take the mean of the bin.
    # NOTE: This the opencv coordinates. max is min here in y-direction.
    u, s, m = np.mean( vec ), np.std( vec ), np.min(vec)
    return m
    cv = s / u
    print( cv, m, u )
    if cv > 0.1:
        return np.median(vec) - s
    return m


def save_debug_imgage( filename, img ):
    if debug_:
        cv2.imwrite( filename, img )

def click_points( event, x, y, flags, params ):
    global img_
    assert img_ is not None, "No data set"
    # Function to record the clicks.
    r, c = img_.shape
    if event == cv2.EVENT_LBUTTONDOWN:
        y = r - y
        logging.info( "MOUSE clicked on %s,%s" % (x,y))
        coords_.append((x, y))


def show_frame( img, msg = 'MSG: ' ):
    global windowName_
    msgImg = np.zeros( shape=(50, img.shape[1]) )
    cv2.putText( msgImg, msg, (1, 40), 0, 0.5, 255 )
    newImg  =  np.vstack( (img, msgImg))
    cv2.imshow( windowName_, newImg )

def ask_user_to_locate_points(points, img):
    global coords_
    cv2.namedWindow( windowName_ )
    cv2.setMouseCallback( windowName_, click_points )
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
    ps = [[float(a) for a in x.split(',')] for x in points]
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
    hist, bins = np.histogram( img.ravel(), 256, [0, 256], density=True )

def extract_trajectories( img ):
    # First some filtering.
    img = filter_plot( img )

def locate_and_erase_axis( img, extra = 0 ):
    # extra: extra rows and cols to erase. Help in containing error near axis.
    global mapping_
    # compute the transformation between old and new axis.
    T = compute_scaling_offset( points_, coords_ )
    r, c = img.shape
    # x-axis and y-axis chopping can be computed by offset.
    offX, offY = T[1]
    offCols, offRows = int(round(offX)), int(round(offY))
    img[r-offRows-extra:, :] = params_[ 'background']
    img[:,:offCols+extra]  = params_['background']
    return T

def find_trajectory( img, pixel, T ):
    res = []
    r, c = img.shape 
    new = np.zeros_like( img )
    Y, X = np.where( img == pixel )
    traj = defaultdict( list )
    for x,y in zip(X, Y):
        traj[x].append( y )

    (sX,sY), (offX, offY) = T
    for k in sorted(traj):
        x = k
        vals = np.array(traj[k])

        # These are in opencv pixles. So there valus starts from the top. 0
        # belogs to top row. Therefore > rather than <.
        vals = vals[ np.where( vals > vals.mean() ) ]
        if  len(vals) == 0:
            print( 'x', end = '' )
            continue

        y = find_center( vals )
        cv2.circle( new, (x,int(y)), 2, 255 )
        x1 = (x - offX)/sX
        y1 = (r - y - offY)/sY
        res.append( (x1, y1) )

    # sort by x-axis.
    res = sorted( res )
    if args_.plot:
        plot_traj( res )
    return res, np.vstack((img,new))

def plot_traj( traj ):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    try:
        mpl.style.use( 'classic' )
    except Exception as e:
        pass
    mpl.rcParams['text.usetex'] = False
    x, y = zip( *traj )
    plt.plot( x, y )
    plt.show()
    plt.close()

def compute_foregrond_background_stats( img ):
    params = {}
    assert img is not None
    hs, bs = np.histogram( img.ravel(), 256//2, [0, 256], normed = True )
    hist = sorted( zip(hs,bs), reverse = True)
    # Most often occuring pixel is backgorund. Second most is likely to be
    # primary trajectory.
    params[ 'histogram_binsize2' ]  = hs
    params[ 'pixel_freq' ]  = hist
    params[ 'background' ] = int( hist[0][1] )
    params[ 'foreground' ] = int(hist[1][1])
    return params

def process( img ):
    global params_
    global args_
    params_ = compute_foregrond_background_stats( img )
    T = locate_and_erase_axis( img, extra = args_.erase_near_axis )
    traj, img = find_trajectory( img, int(params_['foreground']), T)
    save_debug_imgage(os.path.join(temp(),'final.png'), img )
    return traj

def run( args ):
    global coords_, points_
    global img_, args_
    args_ = args

    if args_.debug:
        debug_ = True 

    infile = args.input
    logging.info( 'Got file: %s' % infile )
    img_ = cv2.imread( infile, 0 )

    save_debug_imgage(os.path.join(temp(), '_original.png'), img_ )

    points_ = list_to_points( args.data_point )
    coords_ = list_to_points( args.location )

    if len(coords_) != len(points_):
        logging.debug( "Either location is not specified or their numbers don't"
            " match with given datapoints."
            )
        ask_user_to_locate_points(points_, img_)
    else:
        # User specified coordinates are in opencv axis i.e. top-left is 0,0
        yoffset = img_.shape[0]
        coords_ = [(x, yoffset-y) for (x,y) in coords_]

    traj = process( img_ )

    if args_.plot:
        plot_traj( traj )

    outfile = args.output or '%s.traj.csv' % args.input 
    with open( outfile, 'w' ) as f:
        for r in traj:
            f.write( '%g %g\n' % (r))
    logging.info( "Wrote trajectory to %s" % outfile )

def main():
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
    parser.add_argument('--data-point', '-p'
        , required = True
        , action = 'append'
        , help = 'Please specify a datapoint. You have to manually click them on '
                ' the figure. At least 2 points are required. 3 are recommended. e.g. '
                '   -p 0,0 -p 10,0 -p 0,1 '
                'Make sure that point are comma separated without any space.'
        )
    parser.add_argument('--location', '-l'
        , required = False, default = []
        , action = 'append'
        , help = 'Location of a data-point on figure in pixels (integer).'
                 ' These values should appear in the same order as -p option.'
                 ' If not given, you will be asked to click on the figure.'
        )

    parser.add_argument('--background', '-b'
        , required = False, default = 255, type = int
        , help = 'Background color (grayscale: 0=black, 255=white)'
        )

    parser.add_argument('--foreground', '-f'
        , required = False, default = 0, type = int
        , help = 'Datapoint color (grayscale: 0=black, 255=white)'
        )

    parser.add_argument('--erase_near_axis', '-e'
        , required = False, default = 1
        , type = int 
        , help = 'Number of rows and columns to ignore near both axis.'
        )

    parser.add_argument('--plot'
        , required = False
        , action = 'store_true'
        , help = 'Plot the final result. Requires matplotlib.'
        )

    parser.add_argument('--output', '-o'
        , required = False, type = str
        , help = 'Name of the output file else trajectory will be written to '
                ' <input>.traj.csv'
        )
    parser.add_argument('--debug', '-d'
        , required = False, action = 'store_true'
        , help = 'Debug mode'
        )
    class Args: pass 
    args = Args()
    parser.parse_args(namespace=args)
    run( args )

if __name__ == '__main__':
    main()
