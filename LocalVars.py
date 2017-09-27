# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 00:36:42 2017

@author: pfduc
"""

try:
    
    __import__('PyQt5')
    USE_PYQT5 = True
    print("using PyQt5")
    
except ImportError:
    
    USE_PYQT5 = False
    print("using PyQt4")
    