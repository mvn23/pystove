import os
import sys
from setuptools import setup

sys.path[0:0] = ['pystove']
from version import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pystove",
    version=__version__,
    author="Milan van Nugteren",
    author_email="milan@network23.nl",
    description=("A library to interface with HWAM wood burning stoves."),
    license="GPLv3+",
    keywords="stove hwam smartcontrol",
    url="https://github.com/mvn23/pystove",
    packages=['pystove'],
    long_description=read('README.md'),
    install_requires=[
        'aiohttp',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)"
    ],
)
