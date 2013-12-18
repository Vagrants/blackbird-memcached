#!/usr/bin/env python
# -*- encodig: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='blackbird-memcached',
    version='0.1.0',
    description=(
        'Get stats of memcached for blackbird by using "stats".'
    ),
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='http://ghe.amb.ca.local/Unified/blackbird-memcached',
)
