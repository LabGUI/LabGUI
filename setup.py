#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from unittest import TestLoader

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = [ ]

test_requirements = [ ]

def test_suite():
	return TestLoader().discover('.')

setup(
    author="Bachibouzouk",
    author_email='pfduc@physics.mcgill.ca',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Modular Gui to perform measurements in a low temperature physics laboratory",
    entry_points={
        'console_scripts': [
            'labgui=labgui.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='labgui',
    name='labgui',
    packages=find_packages(include=['labgui']),
    setup_requires=setup_requirements,
    test_suite = 'test_suite', 
    tests_require=test_requirements,
    url='https://github.com/Bachibouzouk/labgui',
    version='0.1.0',
    zip_safe=False,
)
