#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='mathcodegen',
    version='0.0.1',
    description='helpers for opencl metaprograming',
    author=['Christian Schilling', 'Patrik Gebhardt'],
    author_email=['initcrash@gmail.com', 'grosser.knuff@gmail.com'],
    url='http://github.com/initcrash/opencl_meta_tools/',
    download_url='http://github.com/initcrash/opencl_meta_tools/downloads',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    py_modules=[ 'mathcodegen', ],
)
