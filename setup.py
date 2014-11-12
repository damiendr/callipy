#!/usr/bin/env python
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='callipy',
    description='Calling IPython notebooks with arguments',
    long_description=long_description,
    version='0.3.1',
    author='Damien Drix',
    author_email='damien.drix+pypi@gmail.com',
    url='https://github.com/damiendr/callipy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: IPython',
    ],
    py_modules=['callipy'],
    install_requires=[
        "runipy",
        "ipython",
    ],
)

