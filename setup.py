import os

from setuptools import setup

from pystove.version import __version__


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="pystove",
    version=__version__,
    author="Milan van Nugteren",
    author_email="milan@network23.nl",
    description=("A library to interface with HWAM wood burning stoves."),
    license="GPLv3+",
    keywords="stove hwam smartcontrol",
    url="https://github.com/mvn23/pystove",
    packages=["pystove"],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    install_requires=[
        "aiohttp",
        "defusedxml",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 or later " "(GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
