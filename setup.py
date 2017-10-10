#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2017 Ramil Nugmanov <stsouko@live.ru>
#  This file is part of BioStat.
#
#  BioStat
#  is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
from BioStat.version import version
from pathlib import Path
from setuptools import setup, find_packages

setup(
    name='BioStat',
    version=version(),
    packages=find_packages(),
    url='https://github.com/stsouko/BioStat',
    license='AGPLv3',
    author='Dr. Ramil Nugmanov',
    author_email='stsouko@live.ru',
    description='BioStat',
    package_data={'BioStat': ['templates/*.html', 'static/css/*.css', 'static/js/*.js', 'static/favicon.ico']},
    scripts=['biostat.py'],
    install_requires=['flask', 'flask-nav', 'flask-wtf', 'flask-bootstrap', 'pandas', 'scipy'],
    long_description=(Path(__file__).parent / 'README.md').open().read(),
    keywords='BioStat WEB DataAnalysis',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: Chemistry',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 ]
)