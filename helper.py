"""helper.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import pandas as pd
import numpy as np
import cv2
import io
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('classic' )

midline_val_          = 200
midline_straight_val_ = 100

def straighten_frame( frame, midline ):
    global midline_val_
    newframe = np.zeros_like( frame )
    for i, row in enumerate(midline):
        midP = np.where( row == midline_val_ )[0]
        straightMidP = np.where( row == midline_straight_val_)[0]
        if len(midP) > 0 and len(straightMidP) > 0:
            d = midP[0] - straightMidP[0]
            row = np.roll(frame[i], -d)
            newframe[i] = row 
        else:
            newframe[i] = frame[i]
    return newframe


def lines_to_dataframe( lines ):
    cols = 't1,t2,s1,a,b,c,d,e,f,g,h,status,sig1,sig2'.split(',')
    d = pd.read_csv( io.StringIO(lines), sep = ',', names = cols
            , parse_dates = [ 't2', 't1'] )
    # Drop invlid lines.
    d = d.dropna()
    return d 

def get_time_slice( df, status ):
    f = df[df['status'] == status]['t1'].values
    if len(f) > 2:
        return f[0], f[-1]
    return 0, 0

def _max(a, b):
    if a is None:
        return b
    if b is None:
        return a 
    return max(a,b)

def _min(a, b):
    if a is None:
        return b
    if b is None:
        return a 
    return min(a,b)

def _interp( x, x0, y0 ):
    return np.interp(x, x0, y0)


def pad_frame( f, pad, color):
    return np.pad( f, pad_width=pad, mode='constant', constant_values=color)

def pad_frames( frames, pad = 20, color = 255 ):
    return [ pad_frame(f, pad, color) for f in frames ]

def save_frames( frames, outfile ):
    padded = [ pad_frame(f) for f in frames ]
    if len(frames) == 3:
        save_frame( np.dstack( frames ), outfile )
    else:
        save_frame( np.hstack( frames ), outfile )

def create_grid( frame, step ):
    r, c = frame.shape 
    for i in range(0, r, step):
        frame[i,:] = 50
    for i in range(0, c, step):
        frame[:,i] = 50
    return frame

def save_frames( frames, outfile ):
    plt.figure( figsize=(6,8) )
    for i, frame in enumerate(frames):
        ax = plt.subplot( 1, len(frames), i+1 )
        ax.imshow( frame, interpolation = 'none', aspect = 'auto' )
        #  ax.axis( 'off' )

    plt.tight_layout( )
    plt.savefig( outfile )
    plt.close( )
    
def crop_this_frame( newF, thres = 250 ):
    # Remove whitespace.
    crop = [0, 0, 0, 0]
    # top to bottom.
    nrow, ncols = newF.shape
    for i in range(0, nrow, 1):
        if np.mean(newF[i,:]) < thres:
            crop[0] = i
            break

    # bottom to top.
    for i in range(nrow-1, 0, -1):
        if np.mean(newF[i,:]) < thres:
            crop[1] = i
            break

    # left to right.
    for i in range(ncols):
        if np.mean(newF[:,i]) < thres:
            crop[2] = i
            break

    for i in range(ncols-1,0,-1):
        if np.mean(newF[:,i]) < thres:
            crop[3] = i
            break
    
    print( crop, 'x', newF.shape )
    rowA, rowB, colA, colB = crop
    return newF[rowA:rowB,colA:colB] 

def scale_frame( frame, height ):
    ration = height / frame.shape[0] 
    return cv2.resize( frame, (0,0), fx=ration, fy=ration )

def scale_frame_width( frame, width ):
    ration = width / frame.shape[1] 
    return cv2.resize( frame, (0,0), fx=ration, fy=1 )

def rescale( frames, nrows ):
    return [ scale_frame(f, nrows) for f in frames ]
