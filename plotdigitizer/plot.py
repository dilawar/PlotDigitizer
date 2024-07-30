# helper function for plotting.

import typing as T
from pathlib import Path
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
from loguru import logger

from plotdigitizer import common


def show_frame(img, msg="MSG: "):
    msgImg = np.zeros(shape=(50, img.shape[1]))
    cv.putText(msgImg, msg, (1, 40), 0, 0.5, 255)
    newImg = np.vstack((img, msgImg.astype(np.uint8)))
    cv.imshow(common.WindowName_, newImg)


def plot_images(images_with_title):

    total_images = len(images_with_title)
    num_cols = 2
    num_rows = min(1, total_images // num_cols)
    for i, (title, img) in enumerate(images_with_title):
        logger.debug(f"Plotting `{title}` as index {i+1}")
        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(img, interpolation="none")
        plt.axis(False)
        plt.title(title)
    plt.show()


def plot_traj(traj, img, outfile: T.Optional[Path] = None):

    x, y = zip(*traj)
    plt.figure()
    plt.subplot(211)

    for p in common.locations_:
        csize = img.shape[0] // 40
        cv.circle(
            img,
            (int(p.x), int(img.shape[0] - p.y)),
            int(csize),
            (128, 128, 128),
            -1,
        )

    plt.imshow(img, interpolation="none", cmap="gray")
    plt.axis(False)
    plt.title("Original")
    plt.subplot(212)
    plt.title("Reconstructed")
    plt.plot(x, y)
    plt.tight_layout()
    if not str(outfile):
        plt.show()
    else:
        plt.savefig(outfile)
        logger.info(f"Saved to {outfile}")
    plt.close()
