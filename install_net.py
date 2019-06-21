#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created Jun 19th 2019

@author zackorenberg

This script is designed to be a standalone installer for LabGui, to be used indefinitely until a valid replacement (via pip?) is created

This script will determine a install directory (with the help of user input), make sure the prerequisites are installed, clone the git repository, and run the setup script.
"""

import sys
import os
import pip
import logging
import subprocess

REPOSITORY = "git://github.com/LabGUI/LabGUI.git"
DEBUG = True
DEBUG_BRANCH = 'origin/measure-BF'

GIT_WRAPPER = 'gitpython'#''pygit2' # other options are 'gitpython'
# check version
version_info = sys.version_info
if version_info.major != 3:
    print("You must be using python 3. Current version: "+sys.version)
    exit(1)
VER = str(version_info.major)+"."+str(version_info.minor)+"."+str(version_info.micro)

# check if upgrade
if 'upgrade' in sys.argv:
    sys.argv.remove('upgrade')
    UPGRADE = True
else:
    UPGRADE = False
########################################## UTILITY FUNCTIONS ###########################################################
### pip install for python 3 ###
def pip_install(package_name):
    print("Installing " + package_name)
    if UPGRADE:
        reqs = subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name])
    else:
        reqs = subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
    if reqs != 0: # exit code
        print(reqs)
### clear screen ###
def clear_screen():
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
########################################################################################################################
if GIT_WRAPPER == 'pygit2':
    # attempt to import pygit2, if does not exist, install it
    try:
        import pygit2
    except ImportError:
        pip_install('pygit2')
        import pygit2
elif GIT_WRAPPER == 'gitpython':
    try:
        import git
    except ImportError:
        pip_install('gitpython')
        import git


# find path for LabGui
default_path = os.path.join(
                            os.path.expanduser('~'),
                            'Documents',
                            'LabGui'
                           ) + os.sep

path = input("Path to install LabGui: [%s]"%default_path)
if path == '':
    path = default_path
elif not DEBUG:
    path = os.path.abspath(path) + os.sep # make sure there is a seperator there

################## PYGIT2 WRAPPER #################################
if GIT_WRAPPER == 'pygit2':
    try: # check if repository already exists
        repo = pygit2.Repository(os.path.join(path,'.git'))
    except:
        # clone repository to have latest version of LabGui
        print("Cloning repository %s"%REPOSITORY)
        repo = pygit2.clone_repository(REPOSITORY, path)
    finally:
        # change directory to git path
        if DEBUG:
            print("repo set: ", repo)


    # checkout branch if specified or if in debug, checkout debug branch
    if DEBUG:
        try:
            branch = repo.branches[DEBUG_BRANCH]
        except:
            print("%s is an invalid branch"%DEBUG_BRANCH)
            exit(5)
        finally:
            repo.checkout(branch)
    elif len(sys.argv) > 1:
        try:
            branch = repo.branches[sys.argv[1]]
        except:
            print("%s is an invalid branch"%sys.argv[1])
            branch = repo.branches['master']
        finally:
            repo.checkout(branch)
elif GIT_WRAPPER == 'gitpython': #################### GITPYTHON MODULE ################
    # create progress class for verbose output
    GITPYTHON_UPDATES = []
    class GitPython_Progress(git.remote.RemoteProgress):
        def line_dropped(self, line):
            print(line)
            return
            ## with screen refresh
            GITPYTHON_UPDATES.append(line)
        def update(self, *args):
            print(self._cur_line, end='\r',flush=True)
            return
            ## with screen refresh
            clear_screen()
            print("Cloning Repository %s to %s" % (REPOSITORY, path))
            print("\n".join(GITPYTHON_UPDATES+[self._cur_line]))
            #print(self._cur_line)

    try:
        os.mkdir(path)
    except:
        pass

    try:
        repo = git.Repo(path)
    except:
        if os.listdir(path):  # if path is not empty, create empty file and use that
            if os.path.exists(os.path.join(path, 'LabGUI')):
                i = 1
                while os.path.exists(os.path.join(path, 'LabGUI_%d' % i)):
                    i += 1
                path = os.path.join(path, 'LabGUI_%d' % i)
            else:
                path = os.path.join(path, 'LabGUI')
        print("Cloning Repository %s to %s" % (REPOSITORY, path))
        repo = git.Repo.clone_from(REPOSITORY,path,progress=GitPython_Progress())
        print(flush=True)
    finally:
        if DEBUG:
            try:
                repo.git.checkout(DEBUG_BRANCH)
                print(repo.git.branch())
            except:
                print("Error checking out %s"%DEBUG_BRANCH, sys.exc_info())
                exit(5)
        elif len(sys.argv) > 1:
            try:
                repo.git.checkout(sys.argv[1])
            except:
                print("Error checking out %s"%sys.argv[1], sys.exc_info())
                exit(5)
        print(repo.git.branch())
        #print("Current branch is %s"%repo.git.branch().split('\n')[0].split(' ')[-1]) ####
else: ## USING NORMAL GIT ON THE COMMAND LINE
    ## SET COMMANDS
    Commands = []
    if os.path.exists(os.path.join(path, '.git')): # if git repo exists already

        Commands.append('git init')
    elif not os.listdir(path): # if git repo doesnt exist, and path is empty directory
        Commands.append( 'git clone %s %s' % (REPOSITORY,path) )
    else: # if path is not empty, create empty file and use that
        if os.path.exists(os.path.join(path,'LabGUI')):
            i=1
            while os.path.exists(os.path.join(path,'LabGUI_%d'%i)):
                i+=1
            path = os.path.join(path, 'LabGUI_%d'%i)
        else:
            path = os.path.join(path,'LabGUI')
        Commands.append( 'git clone %s %s' % (REPOSITORY, path))
    if DEBUG:
        Commands.append('git checkout %s -q'%DEBUG_BRANCH)
    elif len(sys.argv) > 1:
        Commands.append('git checkout %s -q'%sys.argv[1])
    ## PATH STUFF
    try:  # make the actual directory
        os.mkdir(path)
    except:
        pass
    finally:  # change directory
        os.chdir(path)
    # EXECUTE COMMANDS
    for cmd in Commands:
        exit_code = subprocess.check_call(cmd.split(' '))
        if exit_code != 0:
            print("Error executing %s, returned with exit code %d"(cmd,exit_code))
            while True:
                prompt = input("Continue? [y/n]:")
                if prompt == 'n':
                    exit(3)
                elif prompt == 'y':
                    break
                else:
                    print("Invalid response")
# change current working dir to LabGui root
os.chdir(path)

# run setup.py

resp = subprocess.check_call([sys.executable, 'setup.py', 'install'])

if resp != 0:
    print("Something went wrong, installation failed")
    exit(1)