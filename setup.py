import os
import sys
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

classifiers = [ 'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python3',
    ]

setup(
    name = "PlotDigitizer",
    version = "0.0.5",
    description = "Digitize plots and extract trajectories.",
    long_description = readme,
    long_description_content_type = 'text/markdown',
    packages = [ 'PlotDigitizer' ],
    package_dir = { 'PlotDigitizer' : '.' },
    install_requires = [ 'numpy' ],
    author = "Dilawar Singh",
    author_email = "dilawar.s.rajput@gmail.com",
    url = "http://github.com/dilawar/PlotDigitizer",
    license='GPLv3',
    classifiers=classifiers,
    entry_points = { 'console_scripts' : 'plotdigitizer=PlotDigitizer.plotdigitizer:main' }
)
