# -*- coding: utf-8 -*-
"""
Created on June 17th 2019

@author zackorenberg

This file generates a configuration file based on config_example.txt. This script is to be run on first use of LabGUI, within the root directory of LabGUI.

It will assume that drivers, widgets, and scripts can be found in LabDrivers, LabTools, and scripts respectively. Unless specified otherwise, it will use the default script is script.py, and will copy script_example.py to scripts folder. It will also assume the default settings file is settings\default-settings.txt unless otherwise specified
"""

import os
from shutil import copyfile
import sys

OS = sys.platform
if OS == 'win32':
    WINDOWS = True
else:
    WINDOWS = False
#if OS == 'Win32':
#    JOIN = '\\'
#else:
#    JOIN = '/'
DEBUG = True # for debugging purposes
JOIN = os.sep

CURR_DIR = os.path.abspath(os.curdir)
os.chdir(CURR_DIR)

#print(CURR_DIR)
#print(os.getcwd())
PYTHON_EXEC = os.fspath(sys.executable)



## welcome info ##
print("=== LabGUI config.txt generator===")
if len(sys.argv) > 1:
    if sys.argv[1] == '--relative' or sys.argv[1] == '-r':
        RELATIVE = True
    elif sys.argv[1] == '--absolute' or sys.argv[1] == '-a':
        RELATIVE = False
else:
    print("Current path: "+CURR_DIR)
    while True:
        resp = input("Use relative or absolute path? [r/a]")
        if resp == 'r':
            RELATIVE = True
            break
        elif resp == 'a':
            RELATIVE = False
            break
        else:
            print("Invalid response: "+resp)

if RELATIVE:
    suffix = ''
else:
    suffix = CURR_DIR + os.sep

if os.path.exists(os.path.join(CURR_DIR, "config.txt")) and not DEBUG:
    while True:
        val = input("Configuration file exists. Rewrite? [y/n]")
        if val == 'y':
            REWRITE = True
            break
        elif val == 'n':
            REWRITE = False
            break
        else:
            print("Invalid response")
    if not REWRITE:
        print("Quitting")
        exit(0)

# now to open/create config.txt
if not DEBUG:
    config = open("config.txt","w+")

conf_dict = {}
## Setting data-path ##

path = input("Set data-path ["+suffix+"scratch"+JOIN+"]")
if path == '':
    path = 'scratch'+JOIN
# necessary stuff
if path.startswith(JOIN):
    if WINDOWS or RELATIVE:
        path.lstrip(JOIN)
try:
    os.makedirs(os.path.dirname(path))
except FileExistsError:
    pass
except:
    print(sys.exc_info())

#if not os.path.exists(os.path.dirname(path)):

if not RELATIVE:
    conf_dict['DATA_PATH'] = os.path.abspath(path)
else:
    conf_dict['DATA_PATH'] = path

## scripts file ##

path = input("Default script file ["+suffix+"scripts"+JOIN+"script.py]")
if path == '':
    path = "scripts"+JOIN+"script.py"

# necessary stuff
if path.startswith(JOIN):
    if WINDOWS or RELATIVE:
        path.lstrip(JOIN)
try:
    os.makedirs(os.path.dirname(path))
except FileExistsError:
    pass
except:
    print(sys.exc_info())

# check if file exists
if not os.path.isfile(os.path.abspath(path)) and not DEBUG:
    copyfile("script_example.py", path)

if not RELATIVE:
    conf_dict['SCRIPT'] = os.path.abspath(path)
else:
    conf_dict['SCRIPT'] = path


## setting file ##

path = input("Default settings file ["+suffix+"settings"+JOIN+"settings.txt]")
if path == '':
    path = "settings"+JOIN+"settings.txt"

# necessary stuff
if path.startswith(JOIN):
    if WINDOWS or RELATIVE:
        path.lstrip(JOIN)
try:
    os.makedirs(os.path.dirname(path))
except FileExistsError:
    pass
except:
    print(sys.exc_info())
# check if file exists
if not os.path.isfile(os.path.abspath(path)) and not DEBUG:
    settings = open(os.path.abspath(path), "w+")
    settings.write('dt(s), TIME, , dt')
    settings.close()

if not RELATIVE:
    conf_dict['SETTINGS'] = os.path.abspath(path)
else:
    conf_dict['SETTINGS'] = path


## drivers file ##

path = input("Default drivers folder ["+suffix+"LabDrivers"+JOIN+"]")

if path == '':
    path = 'LabDrivers'+JOIN

if not os.path.exists(path):
    print("NOTE: this directory currently does not exist. ", path)

if not RELATIVE:
    conf_dict['DRIVERS'] = os.path.abspath(path)
else:
    conf_dict['DRIVERS'] = path


## GPIB_INTF
while True:
    gpib_intf = input("GPIB Interface; pyvisa or prologix: [pyvisa]")
    if gpib_intf == '':
        gpib_intf = 'pyvisa'
        break
    elif gpib_intf == 'pyvisa' or gpib_intf == 'prologix':
        break
    else:
        print("Invalid option: "+gpib_intf)

conf_dict['GPIB_INTF'] = gpib_intf

# debug is false by default
conf_dict['DEBUG'] = 'False'

# TODO add userscripts when implemented fully

if DEBUG:
    for key,value in conf_dict.items():
        print(key+"="+value)
else:
    for key,value in conf_dict.items():
        config.write(key+"="+value+"\n") # python will convert it to OS specific line seperator by default
    config.close()