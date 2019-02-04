import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pystove",
    version="0.1a0",
    author="Milan van Nugteren",
    author_email="milan@network23.nl",
    description=("A library to interface with HWAM wood burning stoves."),
    license="GPLv3+",
    keywords="stove hwam smartcontrol",
    url="https://github.com/mvn23/pystove",
    packages=['pystove'],
    long_description=read('README'),
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
