#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from unittest import TestLoader
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess
import sys
import os
from shutil import copyfile, rmtree

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))  # needs to be in this directory!

if sys.platform == 'win32':
    START_FILE = 'StartLabGui.bat'
    END_FILE = os.path.join('bin', 'LabGui.bat')
else:
    START_FILE = 'StartLabGui.sh'
    END_FILE = os.path.join('bin', 'LabGui')  # changed from LabGui.sh to LabGui

if 'install' not in sys.argv:
    try:
        os.mkdir('bin')
    except:  # already exists
        pass

    try:
        with open(END_FILE, 'w+') as f:
            f.close()
    except:
        print(sys.exc_info())
    QUIET = True
else:
    QUIET = False


def make_script():
    # MAKE LAUNCH SCRIPT
    try:
        os.mkdir('bin')
    except:
        pass
    copyfile(START_FILE, END_FILE)


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'virtualenv']

setup_requirements = []

test_requirements = []


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        if QUIET:
            subprocess.check_call([sys.executable, 'setup_new.py', 'quiet'])
        else:
            subprocess.check_call([sys.executable, 'setup_new.py'])
        make_script()
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        if QUIET:
            subprocess.check_call([sys.executable, 'setup_new.py', 'quiet'])
        else:
            subprocess.check_call([sys.executable, 'setup_new.py'])
        make_script()
        install.run(self)


def test_suite():
    return TestLoader().discover('.')


setup(
    author="zackorenberg",
    author_email='zachary.berkson-korenberg@mail.mcgill.ca',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description="Modular Gui to perform measurements in a low temperature physics laboratory",
    # entry_points={
    #    'console_scripts': [
    #        'LabGui=%s'+END_FILE,
    #    ],
    # },
    scripts=[os.path.abspath(END_FILE)],
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='LabGui',
    name='LabGui',
    packages=find_packages(include=['LabGui']),
    setup_requires=setup_requirements,
    test_suite='test_suite',
    tests_require=test_requirements,
    url='https://github.com/labgui/labgui',
    version='0.3.1',
    zip_safe=False,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)


try:
    rmtree('bin')
except:  # means no postdevelop/install script has been run
    pass
