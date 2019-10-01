import os
import sys
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

classifiers = [ 'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ]

setup(
    name = "PlotDigitizer",
    version = "0.0.3",
    description = "Digitize plots and extract trajectories.",
    long_description = readme,
    long_description_content_type = 'text/markdown',
    packages = [ 'PlotDigitizer' ],
    package_dir = { 'PlotDigitizer' : '.' },
    install_requires = [ 'numpy', 'opencv-python' ],
    author = "Dilawar Singh",
    author_email = "dilawars@ncbs.res.in",
    url = "http://github.com/dilawar/PlotDigitizer",
    license='GPLv3',
    classifiers=classifiers,
    entry_points = { 'console_scripts' : 'plotdigitizer=PlotDigitizer.plotdigitizer:main' }
)
