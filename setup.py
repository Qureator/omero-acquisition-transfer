#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Qureator, Inc. All rights reserved.
import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "omero-acquisition-transfer"
DESCRIPTION = "Move acquisition metadata between omero servers"
URL = "https://github.com/qureator/omero-acquisition-transfer"
EMAIL = "yunha.shin@qureator.com"
AUTHOR = "Yunha Shin"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = "1.0.0"

# What packages are required for this module to be executed?
REQUIRED = [
    "omero-py>=5.6.0",
    "ome-types>=0.3.2",
    "tifftools",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


def find_assets():
    assets = {}
    for root, dirs, files in os.walk("omero_voxel/assets/"):
        files = [file for file in files if file[0] != "." and not file.endswith(".py")]
        root = os.path.normpath(root)
        assets[".".join(root.split(os.sep))] = files
    return assets


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_data=find_assets(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
