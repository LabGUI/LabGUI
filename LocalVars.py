# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 00:36:42 2017

@author: pfduc
"""

import sys
import os

repository = os.path.abspath(os.path.curdir)

sys.path.append(repository)

sys.path.append(os.path.join(repository, 'LabDrivers'))

labtools_path = os.path.join(repository, 'LabTools')

sys.path.append(labtools_path)

sys.path.append(os.path.join(labtools_path, 'Display'))
sys.path.append(os.path.join(labtools_path, 'Fitting'))
sys.path.append(os.path.join(labtools_path, 'CoreWidgets'))
sys.path.append(os.path.join(labtools_path, 'UserWidgets'))

try:

    __import__('PyQt5')
    USE_PYQT5 = True
    #print("using PyQt5")

except ImportError:

    USE_PYQT5 = False
    #print("using PyQt4")
