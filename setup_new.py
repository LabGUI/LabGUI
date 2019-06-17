"""
Created on Jun 17th, 2019

@author zackorenberg

This is designed to setup LabGUI for first use on a system. It will determine what operating system is in use, add optionality to create venv, and will generate a configuration file

"""

import sys
import os


operating_system = sys.platform

CURR_DIR = os.path.abspath(os.curdir)
print(CURR_DIR)


if operating_system == 'Win32':
    WINDOWS = True
else:
    print("Set up is currently not supported on "+operating_system)
    WINDOWS = False
    exit(5)


print("=== LabGUI setup on "+operating_system+" ===")