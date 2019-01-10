# -*- coding: utf-8 -*-
"""
Created on Thu Mar 01 19:01:51 2018

@author: pfduc
"""


class DTT_Error(Exception):
    def __init__(self, arg):
        self.message = arg


class ScriptFile_Error(Exception):
    def __init__(self, arg):
        self.message = arg
