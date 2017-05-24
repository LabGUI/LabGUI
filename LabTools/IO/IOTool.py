# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 04:59:28 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file
"""

import numpy as np
#from LabDrivers.Tool import LABDRIVER_PACKAGE_NAME
from importlib import import_module
import logging
import time
import os

CONFIG_FILE="config.txt"

#these are the key words used in the configfile, they are defined here only
SCRIPT_ID = "SCRIPT"
DEBUG_ID = "DEBUG"
SAVE_DATA_PATH_ID = "DATA_PATH"
SETTINGS_ID = "SETTINGS"
LOAD_DATA_FILE_ID = "DATAFILE"
GPIB_INTF_ID = "GPIB_INTF"

def create_config_file(main_dir=None):
    """
    this function generate a generic config file from a given path
    """
    # get home directory of the main programm
    if main_dir == None:
        main_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep

    config_path = os.path.join(main_dir, CONFIG_FILE)
    if os.path.exists(os.path.join(main_dir, CONFIG_FILE)):
        logging.warning(
            "the file config.txt already exists, it will not be erased")
    else:
        of = open(config_path, "w")
        of.write("%s=%sscratch%s\n" % (SAVE_DATA_PATH_ID, main_dir, os.sep))
        of.write("%s=True\n"%(DEBUG_ID))
        of.write("%s=%sscripts%sscript.py\n" % (SCRIPT_ID, main_dir,os.sep))
        of.write("%s=%ssettings%sdemo_dice.txt\n" % (SETTINGS_ID,
                                                     main_dir,os.sep))
        of.write("%s=%sscratch%s\n" % (LOAD_DATA_FILE_ID, main_dir,os.sep))
        of.write("%s=\n"%(GPIB_INTF_ID))
        of.close()
        # COOLDOWN=TEST
        # SAMPLE=sample_name

def save_config_file(data_path=None):
    """
    this function generate a config file from actual settings
    """
    # get home directory of the main programm
    cwd = os.path.dirname(os.path.realpath(__file__))

    config_path = os.path.join(cwd, CONFIG_FILE)
    if os.path.exists(os.path.join(cwd, CONFIG_FILE)):
        logging.warning(
            "the file config.txt already exists, it will not be erased")
    else:
        of = open(config_path, "w")
        if not data_path == None:
            of.write("%s=%s\\\n" % (SAVE_DATA_PATH_ID,data_path))
        of.write("%s=True\n"%(DEBUG_ID))
        of.write("%s=%sscripts\script.py\n" % (SCRIPT_ID, cwd))
        of.write("%s=%ssettings\demo_voltage_AC.set\n" % (SETTINGS_ID, cwd))
        of.write("%s=%sdata\\\n" % (LOAD_DATA_FILE_ID,cwd))
        of.close()


def open_therm_file(config_file_name=CONFIG_FILE):
    """
        returns the filename of output file as it is in the config file
    """
    file_name = "no CONFIG file"
    cooldown = ""
    therm_path = ""
    sample_name = ""
    file_format = ".dat"
    name_formatter = "data_path + time.strftime('%y%m%d') + '_' + cooldown \
+ 'therm'"
    try:
        config_file = open(config_file_name)
        for line in config_file:
            [left, right] = line.split("=")
            left = left.strip()
            right = right.strip()
            if left == "COOLDOWN":
                cooldown = right
                cooldown = cooldown + "_"
    #            print "cooldown " + cooldown
            elif left == "SAMPLE":
                sample_name = right
    #            print "sample " + sample_name
            elif left == "THERM_PATH":                
                data_path = right
            elif left == "DATA_PATH":
                data_path = right
            elif left == "FILE_FORMAT":
                file_format = eval(right)

        # if a separate thermometry path is specified, it will overrule data_path
        if therm_path:
            data_path = therm_path
        try:
            
            file_name = eval(name_formatter)
            
            n = 1
            # make sure the file doesn't already exist by incrementing the
            # number
            while os.path.exists(file_name + "_%3.3d%s" % (n, file_format)):
                n += 1
            file_name = file_name + "_%3.3d%s" % (n, file_format)
        except:
            file_name = "No output file choosen"

        config_file.close()
    except IOError:
        print("No configuration file " + config_file_name + "  found")

    return file_name


def get_file_name(config_file_name=CONFIG_FILE):
    """
        returns the filename of output file as it is in the config file
    """
    file_name = "no CONFIG file"
    cooldown = ""
    therm_path = ""
    sample_name = ""
    file_format = ".dat"
    try:
        config_file = open(config_file_name)
        for line in config_file:
            [left, right] = line.split("=")
            left = left.strip()
            right = right.strip()
            if left == "COOLDOWN":
                cooldown = right
                cooldown = cooldown + "_"
    #            print "cooldown " + cooldown
            elif left == "SAMPLE":
                sample_name = right
    #            print "sample " + sample_name
            elif left == "THERM_PATH":
                therm_path = right
            elif left == SAVE_DATA_PATH_ID:
                data_path = right
            elif left == "FILE_FORMAT":
                file_format = eval(right)

        try:
            file_name = data_path + sample_name + "_" + \
                cooldown + "_" + time.strftime("%m%d")
            file_name = data_path + \
                time.strftime("%y%m%d") + "_" + cooldown + sample_name
            n = 1
            # make sure the file doesn't already exist by incrementing the
            # number
            while os.path.exists(file_name + "_%3.3d%s" % (n, file_format)):
                n += 1
            file_name = file_name + "_%3.3d%s" % (n, file_format)
        except:
            file_name = "No output file choosen"

        config_file.close()
    except IOError:
        print("No configuration file " + config_file_name + "  found")

    return file_name


def get_config_setting(setting, config_file_name = CONFIG_FILE):
    """
        gets a setting from the configuration file
    """
    value = None
    
    try:
        #open the file
        config_file = open(config_file_name,'r')

        #loop through all the lines
        for line in config_file:
            #the setting should have a = sign in the line
            [left, right] = line.split("=")
            
            #separate the setting name from its value
            left = left.strip() #name
            right = right.strip() #value
            
            #if the name corresponds to the setting we want, we read the value
            if left == setting:
                
                value = right
                
        if not value:
            
            print("Configuration file does not contain a'" 
                  + setting + "=' line.")
            print("returning the keyword None")
        config_file.close()
        
    except IOError:
        
        print("No configuration file " + config_file_name + " found")
        value = None
        
    return value

def set_config_setting(setting, setting_value, config_file_name = CONFIG_FILE):
    """
        sets a setting to a given value inside the configuration file
    """
    try:
        #open the file
        config_file = open(config_file_name,'r')
    
        #read the lines into a list
        lines = config_file.readlines()
        
        #loop through all the lines
        for i,line in enumerate(lines):
            #the setting should have a = sign in the line
            try:
                [left, right] = line.split("=")
            
                #separate the setting name from its value
                left = left.strip() #name
                right = right.strip() #value
                
                #if the name corresponds to the setting we want, we write the value
                if left == setting:
                    
                    lines[i]="%s=%s\n"%(setting,setting_value)
            
            except ValueError as e:
                
                if "need more than 1 value to unpack" in e:
                    
                    pass
                
                else:
                   
                    raise e
            
        
        config_file.close()
        
        #reopen the file and write the modified lines
        config_file = open(config_file_name,'w')
        config_file.writelines(lines)
        config_file.close()
        
        print(("The parameter '%s' in the config file was \
successfully changed to %s"%(setting,setting_value)))
        
    except:
        
        logging.error("Could not set the parameter %s to %s in the config \
file located at %s\n"%(setting,setting_value, config_file_name))
        

def get_settings_name():
    return get_config_setting(SETTINGS_ID)


def get_script_name():
    return get_config_setting("SCRIPT")

def get_debug_setting():
    setting = get_config_setting(DEBUG_ID)
    if setting:
        # case insensitive check of the debug setting. get_config_setting already performed strip() of whitespace characters
        if setting.upper() == 'TRUE':
            debug = True
        else:
            debug = False
    else:
        # None was returned: possibly no config file, default to regular (non-debug) mode
        debug = False
    return debug

def get_interface_setting():
    return get_config_setting(GPIB_INTF_ID)


def get_drivers(drivers_path):
    print('DEPRECATED: USE LabDrivers.utils.list_drivers instead.')
    return None


def load_file_linux(fname, splitchar='\t'):
    """
    This one is for Linux
    """
    instr = open(fname, 'r')
    data = []
    for dat in instr:
        if dat[0] != "#":
            lines = dat.split(splitchar)
            nrow = 0
            row = []
            for el in lines:
                nrow = nrow + 1
#                print el
                row.append(float(el))

            data.append(row)
    data = np.array(data)
#    data.reshape(nrow,ncolumn)#,nrow)
    return data


def load_file_windows(fname, splitchar = ', ', headers = True, hdr_only = False):
    """
    This one is for Window
    """

    ifs = open(fname, 'r')
    label = {'hdr' : ""}
    
    LABELS_ID = ['P','I','C']
    
    lines = ifs.readlines()
    
    #useful index to know when we passed the lines with specific information
    end_normal_hdr_idx = len(lines)

    
    for i, line in enumerate(lines):
        
        #if the line starts with a #, it is a comment
        if line[0] == "#":

            #get the label identifier :
            #   P for parameter, 
            #   I for instrument,
            #   C for channel name
            label_id = line[1:2]

            #identify if we have an occurence of a label_id from LABELS_ID
            if label_id in LABELS_ID:
                #get rid of the ' signs and the return lines
                line = line[2:].replace("'", "")
                line = line.strip("\n")
                
                #if the line after this one isn't a label_id one
                #it is going to be ignored
                end_normal_hdr_idx = i
                
            else:
                #get rid of the # at beginning of the line
                line = line[1:]
            
            #assign the header parameters according the the label_id
            if label_id == 'P':
                
                label['param'] = line.split(splitchar)
                    
            elif label_id == 'I':
                
                label['instr'] = line.split(splitchar)
                
            elif label_id == 'C':
                
                label['channel_labels'] = line.split(', u')
                
            #this is user comments we only save the ones that are 
            #before the label_id, other lines will be ignored
            if i < end_normal_hdr_idx:
                
                label['hdr'] = label['hdr'] + line 

    ifs.close()

    #load the data matrix using numpy is faster
    data = np.loadtxt(fname)
    
    #this means there is only the 'hdr' key
    if len(label) == 1:
        
        label['param'] = ["col %i"% i for i in range(np.size(data,1))]

    #return both the data and the header content if header is set to True
    if headers:
        #this means there is only the 'hdr' and 'param' keys
        if len(label) == 2:
            
            print("IOTools.load_file_windows : #P, #I or #C headers are \
missing, all lines starting with # are available in the second output dict")
        
        return data, label
    
    else:
        
        return data


def load_pset_file(fname, labels=None, splitchar=' '):
    """
        gets the channels ticks for a plot
    """
    fname = str(fname)
    if not fname.find('.') == -1:
        fname = fname[0:fname.find('.')] + '.pset'

    all_ticks = []
    for setting in ['X', 'YL', 'YR']:
        #        print "set",setting
        ticks = []
        try:
            pset_file = open(fname)
            for line in pset_file:
                [left, right] = line.split("=")
                left = left.strip()
                right = right.strip()
#                print left
                if left == setting:
                    #                    print right
                    ticks = (right.split(','))

            pset_file.close()
        except IOError:
            print("IOTool.load_pset_file : No file " + fname + "  found")

        if labels:
            for i, t in enumerate(ticks):
                if t in labels:
                    ticks[i] = labels.index(t)
                else:
                    print("\n the tick " + " does not correspond to a label in the list")
                    print(labels)
                    print("\n")
        if setting == 'X':
            if len(ticks):
                ticks = ticks[0]
            else:
                ticks = ''
        all_ticks.append(ticks)

    return all_ticks


def load_aset_file(fname, splitchar=':'):
    """
    This one is for Window
    """
    instr = open(fname, 'r')
    bounds = []
    physparam = []
    fitparam = []
    physparam_val = []
    fitparam_val = []
#    label={}
    for dat in instr:
        #        print dat
        if dat[0] != "#":
            #            print dat

            lines = dat.strip('\n')
            lines = lines.split(splitchar)
#            print lines
            bounds.append(lines[0].split(','))
            physparam_val.append(lines[1].strip('\t').split('\t'))
            fitparam_val.append(lines[2].strip('\t').split('\t'))
        else:
            lines = dat[1:len(dat) - 1].strip('\n')
            lines = lines.split(splitchar)
            physparam.append(lines[0].strip('\t').split('\t'))
            fitparam.append(lines[1].strip('\t').split('\t'))
#            for i,el in enumerate(lines):
#                if not el=='':
#                    lines[i]=float(el)
#            lines=lines[0:len(lines)-1]
#            print lines
#            nrow=0
#    print bounds,physparam_val,fitparam
    return bounds, physparam_val, fitparam_val, physparam, fitparam


def load_adat_file(fname, splitchar=' '):
    """
    This one is for Window
    """
    instr = open(fname, 'r')
    data = []
#    label={}
    for dat in instr:
        #        print dat
        if dat[0] != "#":
            #            print dat

            lines = dat.strip('\n')
            lines = lines.split('\t')

            for i, el in enumerate(lines):
                if not el == '':
                    lines[i] = float(el)
            lines = lines[0:len(lines) - 1]
            print(lines)

            data.append(lines)
        else:
            dat = dat[1:len(dat)].replace("'", "")
            dat = dat.strip("\n")
            line = dat.split(' ')
#            print line
            param_id = line[0]

            if param_id == 'BKG_P':
                B_P = line[1].split('\t')
            elif param_id == 'BKG_V':
                B_V = line[1].split('\t')
            elif param_id == 'P':
                P = line[1].split('\t')

    parameters = {}
    for bp, bv, p in zip(B_P, B_V, P):
        if not bp == '':
            parameters[bp] = bv
    print(parameters)
    data = np.array(data)
    data[:, 0] = data[:, 0] - float(B_V[0])
    data[:, 1] = data[:, 1] - float(B_V[1])
    print("the background values are substracted")
    return data
#    data.reshape(nrow,ncolumn)#,nrow)


def import_module_func(module_name, func_name, package=None):
    """
    given a module and a function name (in strings) 
    it returns a function handle
    """
    my_module = import_module(module_name, package=package)
    return getattr(my_module, func_name)


def get_func_variables(my_func):
    """
    given a function handle, this function returns the latter variable names
    """
#    print my_func.func_code.co_varnames
    return my_func.__code__.co_varnames


def list_module_func(module_name, package = None):
    """
    given a module name which is in the PYTHONPATH this function 
    lists all the function names of the module
    """
    my_module = import_module(module_name, package=package)
    all_funcs = dir(my_module)
    my_funcs = []
    for func in all_funcs:
        #        print func
        #        print func[0:2]
        # discriminate the function that have __ in front of them
        if not func[0:2] == "__":
            my_funcs.append(func)
    return my_funcs


def save_matrix(M):
    np.savetxt('matrix.dat', M)
#    scipy.io.savemat('matrix.mat',mdict={'out': M},oned_as='row')


def match_value2index(array1D, val):
    """
    this function will find the index of a value in an array
    if there is no match it will return the index of the closest value
    """

    my_array = array1D
    Nmax = len(my_array) - 1

    if val > my_array[Nmax]:
        index = Nmax
    elif val < my_array[0]:
        index = 0
    else:
        if val in my_array:
            index = np.where(my_array == val)[0][0]
        else:
            index = np.where(my_array > val)[0][0]
            if not index:
                index = max(np.where(my_array < val)[0])
    return index


if __name__ == "__main__":
    import time
    ts = time.time()
    d,l = load_file_windows("test_load.dat")
    print l
    print time.time()-ts
