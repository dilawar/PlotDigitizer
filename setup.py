import os
import sys
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name = "PlotDigitizer",
    version = "0.1.0",
    description = "Digitize plots and extract trajectories.",
    long_description = readme,
    long_description_content_type = 'text/markdown',
    packages = [ 'PlotDigitizer' ],
    package_dir = { 'PlotDigitizer' : '.' },
    install_requires = [ 'numpy', 'loguru' ],
    author = "Dilawar Singh",
    author_email = "dilawar.s.rajput@gmail.com",
    url = "http://github.com/dilawar/PlotDigitizer",
    license='GPLv3',
    entry_points = { 'console_scripts' : 'plotdigitizer=PlotDigitizer.plotdigitizer:main' }
)
