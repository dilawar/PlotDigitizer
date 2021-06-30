__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import numpy as np
import cv2 as cv


def _find_center(vec):
    return np.median(vec)


def fit_trajectory_using_median(traj, T, img):
    (sX, sY), (offX, offY) = T
    res = []
    r, _ = img.shape

    # x, y = zip(*sorted(traj.items()))
    # logger.info((xvec, ys))

    for k in sorted(traj):
        x = k

        vals = np.array(traj[k])

        # For each x, we may multiple pixels in column of the image which might
        # be y. Usually experience is that the trajectories are close to the
        # top rather to the bottom. So we discard call pixel which are below
        # the center of mass (median here)
        # These are opencv pixles. So there valus starts from the top. 0
        # belogs to top row. Therefore > rather than <.
        avg = np.median(vals)
        vals = vals[np.where(vals >= avg)]
        if len(vals) == 0:
            continue

        # Still we have multiple candidates for y for each x.
        # We find the center of these points and call it the y for given x.
        y = _find_center(vals)
        cv.circle(img, (x, int(y)), 1, 255, -1)
        x1 = (x - offX) / sX
        y1 = (r - y - offY) / sY
        res.append((x1, y1))

    # sort by x-axis.
    return sorted(res)