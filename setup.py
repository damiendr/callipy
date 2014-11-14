#!/usr/bin/env python
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
readme = path.join(here, 'README.md')
try:
    from pypandoc import convert
    long_description = convert(readme, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    with open(readme, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='callipy',
    description='Calling IPython notebooks with arguments',
    long_description=long_description,
    version='0.3.2',
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

