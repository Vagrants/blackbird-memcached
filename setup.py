#!/usr/bin/env python
# -*- encodig: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='blackbird-memcached',
    version='0.1.5',
    description=(
        'Get stats of memcached for blackbird by using "stats".'
    ),
    long_description=read('PROJECT.txt'),
    classifiers=[
      'Development Status :: 4 - Beta',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.6',
    ],
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='https://github.com/Vagrants/blackbird-memcached',
    data_files=[
        ('/opt/blackbird/plugins', ['memcached.py']),
        ('/etc/blackbird/conf.d', ['memcached.cfg'])
    ],
)
