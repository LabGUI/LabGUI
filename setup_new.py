"""
Created on Jun 17th, 2019

@author zackorenberg

This is designed to setup LabGUI for first use on a system. It will determine what operating system is in use, add optionality to create venv, and will generate a configuration file

"""

import sys
import os
import pip
import logging

try:
    import virtualenv
    VIRTUALENV_MODULE = True
except:
    VIRTUALENV_MODULE = False

import subprocess

UPGRADE = False
if '--upgrade' in sys.argv or 'upgrade' in sys.argv:
    UPGRADE = True

QUIET = False
if 'quiet' in sys.argv or True in ['wheel' in i for i in sys.argv] or True in ['dist' in i for i in sys.argv]:
    QUIET = True
    def input(variable):
        return 'y'


### pip install for python 3 ###
def pip_install(package_name):
    print("Installing "+package_name)
    if UPGRADE:
        reqs = subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name])
    else:
        reqs = subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
    print(reqs)

#pip_install('scipy')
#exit(0)

operating_system = sys.platform

CURR_DIR = os.path.abspath(os.curdir)
#print(CURR_DIR)
os.chdir(CURR_DIR)

MAIN_FILE = 'LabGui.py'

if operating_system == 'win32':
    WINDOWS = True
else:
    print("Set up is currently not supported on %s. Use at your own discretion."%operating_system)
    while True:
        cont = input("Continue? [y/n]:")
        if cont == 'y':
            break
        elif cont == 'n':
            exit(0)
        else:
            print("Invalid selection.")
    WINDOWS = False

DEBUG = False

if DEBUG:
    log_lvl = logging.DEBUG
else:
    log_lvl = logging.INFO

VENV_CLEAR = True #clears virtual event
JOIN = os.sep

NEWLINE = '\n'

version_info = sys.version_info
if version_info.major != 3:
    print("You must be using python 3. Current version:"+sys.version)
    exit(1)
VER = str(version_info.major)+str(version_info.minor)

#print(CURR_DIR)
#print(os.getcwd())
if hasattr(os, "fspath") and callable(os.fspath):
    PYTHON_EXEC = os.fspath(sys.executable)
else:
    PYTHON_EXEC = os.path.abspath(sys.executable)


print("=== LabGUI setup on "+operating_system+" ===")
virtual_instructions = []
virtual_instructions.append("If you wish to use a virtual environment, call the following commands")
virtual_instructions.append("\t$ pip install virtualenv")
virtual_instructions.append("\t$ cd "+CURR_DIR)
virtual_instructions.append("\t$ virtualenv venv"+VER)

try: # THE FOLLOWING CHANGE MAKES THIS DYNAMIC REGARDLESS OF OS
    venv_bin_dir = os.path.relpath(virtualenv.path_locations("venv"+VER, dry_run=True)[-1])
    if WINDOWS:
        venv_exec = os.path.join(venv_bin_dir, "python.exe")
        venv_activate = os.path.join(venv_bin_dir, "activate")
    else:
        venv_exec = os.path.join(venv_bin_dir, "python")
        venv_activate = os.path.join(venv_bin_dir, "activate")
except: # INCASE PATH HAS SPACES IN IT
    if WINDOWS:
        venv_exec = "venv"+VER+JOIN+"Scripts"+JOIN+"python.exe"
        venv_activate = "venv"+VER+JOIN+"Scripts"+JOIN+"activate"
    else:
        venv_exec = "venv"+VER+JOIN+"bin"+JOIN+"python"
        venv_activate = "source venv"+VER+JOIN+"bin"+JOIN+"activate"
# CHANGE COMPLETE
virtual_instructions.append("Then run this setup file by:")
virtual_instructions.append("\t$ "+os.path.abspath(os.path.join(CURR_DIR,venv_exec))+" "+os.path.relpath(sys.argv[0]))
virtual_instructions.append("- or -")
virtual_instructions.append("\t$ "+venv_activate)
virtual_instructions.append("\t$ python "+os.path.relpath(sys.argv[0]))
# check if running in virtual environment #
if venv_exec in PYTHON_EXEC:
    print("Using virtual environment venv"+VER)
else:
    if os.path.isfile(venv_exec):
        #print("Activating virtual environment")
        cont = input("Activate virtual environment located at %s? [y/n]:"%venv_exec)
        if cont == 'n':
            VIRTUAL = False
        else:
            exec(open(venv_activate + "_this.py").read())
            sys.executable = os.path.abspath(venv_exec)
            VIRTUAL = True
    else:
        while True:
            cont = input("Automatically generate virtual environment? [y/n]:")
            if cont == 'n':
                print("Continuing on "+os.path.dirname(PYTHON_EXEC))
                VIRTUAL = False
                print(NEWLINE)
                for instruction in virtual_instructions:
                    print(instruction)
                break
            elif cont == 'y':
                if not VIRTUALENV_MODULE:
                    print("Installing virtualenv")
                    pip_install('virtualenv')
                    try:
                        import virtualenv
                    except ImportError:
                        print("Please rerun this script")
                        exit(0)
                venv_dir = os.path.join(CURR_DIR,"venv"+VER)
                # the following line was taken almost directly out of virtualenv.py for verbosity #
                virtualenv.logger = virtualenv.Logger([(log_lvl, sys.stdout)])
                # create actual virtualenv
                virtualenv.create_environment(venv_dir, clear=VENV_CLEAR)
                # activate virtualenv
                exec(open(venv_activate+"_this.py").read())
                # update sys.executable (needed)
                sys.executable = os.path.abspath(venv_exec)
                print(sys.executable)
                VIRTUAL = True
                break
            else:
                print("Invalid response: "+cont)


print(NEWLINE)
if hasattr(os, "fspath") and callable(os.fspath):
    PYTHON_EXEC = os.fspath(sys.executable)
else:
    PYTHON_EXEC = os.path.abspath(sys.executable)


print("Current python executable: "+PYTHON_EXEC)

cont = input("Continue? [y/n]:")
if cont != 'y':
    exit(0)

print("Installing requirements")
reqs = []
requirements = open("requirements.txt",'r')
reqs = [i.rstrip('\n') for i in requirements.readlines()]
requirements.close()

for i in reqs:
    pip_install(i)


print(NEWLINE)
print("Generating launcher")

LAUNCH_PATH = os.path.join(CURR_DIR, MAIN_FILE)
if " " in LAUNCH_PATH: # FIX FOR SPACES
    LAUNCH_PATH = "\""+LAUNCH_PATH+"\""
if " " in PYTHON_EXEC:
    PYTHON_EXEC = "\""+PYTHON_EXEC+"\""
if WINDOWS:
    launcher = open("StartLabGui.bat",'w+')
    launcher.write(PYTHON_EXEC + " " + LAUNCH_PATH)
    launcher.close()
    LAUNCHER_FILE = 'StartLabGui.bat'
else:
    launcher = open("StartLabGui.sh", 'w+')
    launcher.write("#!/bin/sh\n")
    launcher.write(PYTHON_EXEC + " " + LAUNCH_PATH)
    launcher.close()
    try:
        subprocess.call("chmod +x StartLabGui.sh".split(" "))
    except:
        pass
    LAUNCHER_FILE = 'StartLabGui.sh'

print("Launcher is "+LAUNCHER_FILE)

cont = input("Create config.txt? [y/n]:")

if cont == 'y':
    import config_generate
print(NEWLINE)
cont = input("Setup complete. Launch LabGui? [y/n]")
if cont == 'y':
    print("Launching LabGui")
    subprocess.call([os.path.join(CURR_DIR, LAUNCHER_FILE)])


