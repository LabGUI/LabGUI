# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 04:59:28 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file
"""

import numpy as np
from importlib import import_module
import logging
import time
import os

# the configuration file will always be in the parent of the parent of the
# directory where this module is located. i.e. in the LabGUI main folder
abs_file = os.path.abspath(os.path.dirname(__file__))
MAIN_DIR = os.sep.join(abs_file.split(os.sep)[:-2]) + os.sep
CONFIG_FILE = "config.txt"
CONFIG_FILE_PATH = MAIN_DIR + CONFIG_FILE


# these are the key words used in the configfile, they are defined here only
SCRIPT_ID = "SCRIPT"
DEBUG_ID = "DEBUG"
SAVE_DATA_PATH_ID = "DATA_PATH"
SETTINGS_ID = "SETTINGS"
WIDGETS_ID = "USER_WIDGETS"
LOAD_DATA_FILE_ID = "DATAFILE"
GPIB_INTF_ID = "GPIB_INTF"
VISA_BACKEND_ID = "VISA_BACKEND"




VISA_BACKEND_DEFAULT = '@ni'
VISA_BACKEND_OPTIONS = ['@ni', '@py']

INTERFACE_DEFAULT = 'pyvisa'
INTERFACE_OPTIONS = ['pyvisa','prologix']
def create_config_file(config_path=CONFIG_FILE_PATH):
    """
    this function generate a generic config file from a given path
    """

    if os.path.exists(config_path):
        logging.warning(
            "the file config.txt already exists, it will not be overwritten")
    else:
        of = open(config_path, "w")
        of.write("%s=%sscratch%s\n" % (SAVE_DATA_PATH_ID, MAIN_DIR, os.sep))
        of.write("%s=False\n" % DEBUG_ID)
        of.write("%s=%sscripts%sscript.py\n" % (SCRIPT_ID, MAIN_DIR, os.sep))
        of.write("%s=%ssettings%sdemo_dice.txt\n" % (SETTINGS_ID,
                                                     MAIN_DIR, os.sep))
        of.write("%s=%sscratch%s\n" % (LOAD_DATA_FILE_ID, MAIN_DIR, os.sep))
        of.write("#%s=prologix or pyvisa\n" % GPIB_INTF_ID)
        of.write("#%s=user_widget1;user_widget2\n" % WIDGETS_ID)
        of.close()


def save_config_file(data_path=None):
    """
    this function generate a config file from actual settings
    """

    if os.path.exists(CONFIG_FILE_PATH):
        logging.warning(
            "the file config.txt already exists, it will not be overwritten")
    else:
        of = open(CONFIG_FILE_PATH, "w")
        if data_path is not None:
            of.write("%s=%s\\\n" % (SAVE_DATA_PATH_ID, data_path))
        of.write("%s=True\n" % DEBUG_ID)
        of.write("%s=%sscripts\script.py\n" % (SCRIPT_ID, MAIN_DIR))
        of.write("%s=%ssettings\demo_voltage_AC.set\n" %
                 (SETTINGS_ID, MAIN_DIR))
        of.write("%s=%sdata\\\n" % (LOAD_DATA_FILE_ID, MAIN_DIR))
        of.close()

def _read_config_file(config_file_path=CONFIG_FILE_PATH):
    ret = ""
    with open(CONFIG_FILE_PATH, 'r') as file:
        ret = file.read()
        file.close()
    return ret

def _write_config_file(raw_text, config_file_path=CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH, 'w+') as file:
        file.write(raw_text)
        #file.writelines(raw_text.split('\n'))

def open_therm_file(config_file_name='config.txt'):
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

        # if a separate thermometry path is specified, it will overrule
        # data_path
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


def get_file_name(config_file_path=CONFIG_FILE_PATH):
    """
        returns the filename of output file as it is in the config file
    """
    file_name = "no CONFIG file"
    cooldown = ""
    therm_path = ""
    sample_name = ""
    file_format = ".dat"
    data_path = ""
    try:

        config_file = open(config_file_path, 'r')

        for line in config_file:

            [left, right] = line.split("=")
            left = left.strip()
            right = right.strip()

            if left == "COOLDOWN":
                cooldown = right
                cooldown = cooldown + "_"
            elif left == "SAMPLE":
                sample_name = right
            elif left == "THERM_PATH":
                therm_path = right
            elif left == SAVE_DATA_PATH_ID:
                data_path = right
                #print(right)
                #if not os.path.isabs(right):
                #    data_path = os.path.abspath( right)
                #    print(data_path)
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
        print("No configuration file " + config_file_path + "  found")

    return file_name

def get_funct_save_name(device, funct, config_file_path=CONFIG_FILE_PATH):
    """
            returns the filename of output file as it is in the config file
        """
    file_name = "no CONFIG file"
    cooldown = ""
    therm_path = ""
    sample_name = ""
    file_format = ".dat"
    data_path = ""

    device = device.replace(" ","") #remove whitespaces
    funct = funct.replace(" ","")
    try:

        config_file = open(config_file_path, 'r')

        for line in config_file:

            [left, right] = line.split("=")
            left = left.strip()
            right = right.strip()

            if left == "COOLDOWN":
                cooldown = right
                cooldown = cooldown + "_"
            elif left == "SAMPLE":
                sample_name = right
            elif left == "THERM_PATH":
                therm_path = right
            elif left == SAVE_DATA_PATH_ID:
                data_path = right
            elif left == "FILE_FORMAT":
                file_format = eval(right)

        try:


            file_name = data_path + \
                        device + "_" + funct + "_" + \
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
        print("No configuration file " + config_file_path + "  found")

    return file_name

def get_config_setting(setting, config_file_path=CONFIG_FILE_PATH):
    """
        gets a setting from the configuration file
    """
    value = None

    try:
        # open the file
        config_file = open(config_file_path, 'r')

        # loop through all the lines
        for line in config_file:

            # the dash caracter is used as comment
            if line[0] != '#':

                # the setting should have a = sign in the line
                [left, right] = line.split("=")

                # separate the setting name from its value
                left = left.strip()  # name
                right = right.strip()  # value

                # if the name corresponds to the setting we want,
                # we read the value
                if left == setting:
                    value = right

        if not value:

            logging.debug("Configuration file does not contain a'"
                          + setting + "=' line.")
            logging.debug("returning the keyword None")

        config_file.close()

    except IOError:

        print("No configuration file " + config_file_path + " found")
        value = None

    except ValueError as e:

        # if this is this error it means the command .split failed and
        # it is likely due to the fact that the file doesn't have the config
        # file format
        if "too many values to unpack" in e:

            err = IOError("The configuration file doesn't have the \
right format")
            raise err
        else:

            raise e

    return value


def set_config_setting(
        setting,
        setting_value,
        config_file_path=CONFIG_FILE_PATH
):
    """
        sets a setting to a given value inside the configuration file
    """
    try:
        # open the file
        config_file = open(config_file_path, 'r')

        # read the lines into a list
        lines = config_file.readlines()

        # loop through all the lines
        for i, line in enumerate(lines):
            # the setting should have a = sign in the line
            try:
                [left, _] = line.split("=")

                # separate the setting name from its value
                left = left.strip()  # name

                # if the name corresponds to the setting we want,
                # we write the value
                if left == setting:

                    lines[i] = "%s=%s\n" % (setting, setting_value)

            except ValueError as e:

                if "need more than 1 value to unpack" in e:

                    pass

                else:

                    raise e

        config_file.close()

        # reopen the file and write the modified lines
        config_file = open(config_file_path, 'w')
        config_file.writelines(lines)
        config_file.close()

        logging.info(("The parameter '%s' in the config file was \
successfully changed to %s" % (setting, setting_value)))

    except:

        logging.error("Could not set the parameter %s to %s in the config \
file located at %s\n" % (setting, setting_value, config_file_path))

def get_save_file_path(**kwargs):
    return get_config_setting(SAVE_DATA_PATH_ID, **kwargs)
def set_save_file_path(path, **kwargs):
    set_config_setting(SAVE_DATA_PATH_ID, path, **kwargs)
def get_settings_name(**kwargs):
    return get_config_setting(SETTINGS_ID, **kwargs)

def set_settings_name(settings_name, **kwargs):
    set_config_setting(SETTINGS_ID, settings_name, **kwargs)

def get_user_widgets(**kwargs):
    """ collect the widget names the user would like to run"""
    widgets = get_config_setting(WIDGETS_ID, **kwargs)
    if widgets is None:
        return []
    else:
        return widgets.split(';')

def set_user_widgets(widgets, **kwargs):
    """ set user widgets, in form of list """
    if type(widgets) != list:
        widgets = [widgets]
    set_config_setting(WIDGETS_ID, ";".join(widgets), **kwargs)

def get_script_name(**kwargs):
    return get_config_setting("SCRIPT", **kwargs)

def set_script_name(script_name, **kwargs):
    set_config_setting("SCRIPT", script_name, **kwargs)


def get_debug_setting(**kwargs):
    setting = get_config_setting(DEBUG_ID, **kwargs)
    if setting:
        # case insensitive check of the debug setting. get_config_setting
        # already performed strip() of whitespace characters
        if setting.upper() == 'TRUE':
            debug = True
        else:
            debug = False
    else:
        # None was returned: possibly no config file,
        # default to regular (non-debug) mode
        debug = False
    return debug


def get_interface_setting(**kwargs):
    return get_config_setting(GPIB_INTF_ID, **kwargs)
def set_interface_setting(setting, **kwargs):
    set_config_setting(GPIB_INTF_ID, setting, **kwargs)

def get_visa_backend_setting(**kwargs):
    """
        This function returns the backend which will be input into visa.ResourceManager(backend)
        
        @ni uses national instruments backend (proprietary)
        @py uses pure python pyvisa backend (open source)
        
        NOTE: py requires other packages to be installed, such as linux-gpib, pyusb, pyserial, etc, etc
        
        If not specified in config.txt, VISA_BACKEND_DEFAULT will be used
    """
    backend = get_config_setting(VISA_BACKEND_ID, **kwargs)
    if backend is None:
        backend = VISA_BACKEND_DEFAULT

    if not backend.startswith('@'):
        backend = '@' + backend.lower()

    return backend

def set_visa_backend_settings(backend, **kwargs):
    """
        No intention of saving with @ symbol
    """
    backend = backend.lstrip('@').rstrip('\n').lower()
    set_config_setting(VISA_BACKEND_ID, backend, **kwargs)

def get_drivers(_):
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


def load_file_windows(fname, splitchar=', ', headers=True):
    """
    This one is for Window
    """

    ifs = open(fname, 'r')
    label = {'hdr': ""}

    labels_id = ['P', 'I', 'C', 'D']

    lines = ifs.readlines()

    # useful index to know when we passed the lines with specific information
    end_normal_hdr_idx = len(lines)

    for i, line in enumerate(lines):

        # if the line starts with a #, it is a comment
        if line[0] == "#":

            # get the label identifier :
            #   P for parameter,
            #   I for instrument,
            #   C for channel name
            label_id = line[1:2]

            # identify if we have an occurence of a label_id from LABELS_ID
            if label_id in labels_id:
                # get rid of the ' signs and the return lines
                line = line[2:].replace("'", "")
                line = line.strip("\n")

                # if the line after this one isn't a label_id one
                # it is going to be ignored
                end_normal_hdr_idx = i

            else:
                # get rid of the # at beginning of the line
                line = line[1:]

            # assign the header parameters according the the label_id
            if label_id == 'P':

                label['param'] = line.split(splitchar)

            elif label_id == 'I':

                label['instr'] = line.split(splitchar)

            elif label_id == 'C':

                # old file were saved that way
                label['channel_labels'] = line.split(', u')

                if len(label['channel_labels']) == 1:

                    label['channel_labels'] = \
                        label['channel_labels'][0].split(splitchar)

                else:

                    label['channel_labels'][0] = \
                        label['channel_labels'][0][1:]

            elif label_id == 'D':
                if 'data' not in label.keys():
                    label['data'] = []
                label['data'].append(line.split(', '))

            # this is user comments we only save the ones that are
            # before the label_id, other lines will be ignored
            if i < end_normal_hdr_idx:

                label['hdr'] = label['hdr'] + line.lstrip(' ')

    ifs.close()

    # load the data matrix using numpy is faster
    data = np.loadtxt(fname)

    # this means there is only the 'hdr' key
    if len(label) == 1:

        label['param'] = ["col %i" % i for i in range(np.size(data, 1))]

    # return both the data and the header content if header is set to True
    if headers:
        # this means there is only the 'hdr' and 'param' keys
        if len(label) == 2:

            print("IOTools.load_file_windows : #P, #I or #C headers are \
missing, all lines starting with # are available in the second output dict")

        return data, label

    else:

        return data, {}


def load_pset_file(fname, labels=None):
    """
        gets the channels ticks for a plot
    """
    fname = str(fname)
    if not fname.find('.') == -1:
        fname = fname[0:fname.find('.')] + '.pset'

    all_ticks = []
    for setting in ['X', 'YL', 'YR']:
        ticks = []
        try:
            pset_file = open(fname)
            for line in pset_file:
                [left, right] = line.split("=")
                left = left.strip()
                right = right.strip()
                if left == setting:
                    ticks = (right.split(','))

            pset_file.close()
        except IOError:
            print("IOTool.load_pset_file : No file " + fname + "  found")

        if labels:
            for i, t in enumerate(ticks):
                if t in labels:
                    ticks[i] = labels.index(t)
                else:
                    print("\n the tick " +
                          " does not correspond to a label in the list")
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
    for dat in instr:
        if dat[0] != "#":
            lines = dat.strip('\n')
            lines = lines.split(splitchar)
            bounds.append(lines[0].split(','))
            physparam_val.append(lines[1].strip('\t').split('\t'))
            fitparam_val.append(lines[2].strip('\t').split('\t'))
        else:
            lines = dat[1:len(dat) - 1].strip('\n')
            lines = lines.split(splitchar)
            physparam.append(lines[0].strip('\t').split('\t'))
            fitparam.append(lines[1].strip('\t').split('\t'))
    return bounds, physparam_val, fitparam_val, physparam, fitparam


def load_adat_file(fname):
    """
    This one is for Window
    """
    instr = open(fname, 'r')
    data = []
    for dat in instr:
        if dat[0] != "#":

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
            param_id = line[0]

            if param_id == 'BKG_P':
                bkg_p = line[1].split('\t')
            elif param_id == 'BKG_V':
                bkg_v = line[1].split('\t')
            elif param_id == 'P':
                pressure = line[1].split('\t')

    parameters = {}
    for bp, bv, p in zip(bkg_p, bkg_v, pressure):
        if not bp == '':
            parameters[bp] = bv
    print(parameters)
    data = np.array(data)
    data[:, 0] = data[:, 0] - float(bkg_v[0])
    data[:, 1] = data[:, 1] - float(bkg_v[1])
    print("the background values are substracted")
    return data


def import_module_func(module_name, func_name, package=None):
    """
    given a module and a function name (in strings) 
    it returns a function handle
    """
    my_module = import_module(module_name, package=package)
    return getattr(my_module, func_name)
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
    return my_func.__code__.co_varnames


def list_module_func(module_name, package=None):
    """
    given a module name which is in the PYTHONPATH this function 
    lists all the function names of the module
    """
    try:

        my_module = import_module(module_name, package=package)

    except ImportError as e:

        if package is None:

            print(
                "You didn't specify a package maybe the error stems from that"
            )

        else:

            print("The module %s in not in the package %s" % (module_name,
                                                              package))

        raise e

    all_funcs = dir(my_module)
    my_funcs = []

    for func in all_funcs:
        # discriminate the function that have __ in front of them
        if not func[0:2] == "__":

            my_funcs.append(func)

    return my_funcs

def list_user_widgets():
    path = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(path, "UserWidgets")
    return [
        o.rstrip(".py")
        for o in os.listdir(path)
        if o.endswith(".py") and "__init__" not in o
    ]
def list_interface_options():
    return ['pyvisa', 'prologix']

def save_matrix(matrix_m):
    np.savetxt('matrix.dat', matrix_m)
#    scipy.io.savemat('matrix.mat',mdict={'out': M},oned_as='row')


def match_value2index(array1D, val):
    """
    this function will find the index of a value in an array
    if there is no match it will return the index of the closest value
    """

    my_array = array1D
    n_max = len(my_array) - 1

    if val > my_array[n_max]:
        index = n_max
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

CONFIG_OPTIONS = {
    SCRIPT_ID : {
        "get" : get_script_name,
        "set" : set_script_name,
        "type": 'file',
        "name": "Default Script"
    },
    SAVE_DATA_PATH_ID : {
        "get" : get_save_file_path,
        "set" : set_save_file_path,
        "type": 'path',
        "name": "Save Data Path"
    },
    SETTINGS_ID : {
        "get" :  get_settings_name,
        "set" : set_settings_name,
        "type" : 'file',
        "name" : "Settings File"
    },
    WIDGETS_ID : {
        "get" :  get_user_widgets,
        "set" : set_user_widgets,
        "default" : None,
        "options" : list_user_widgets(),
        "reset" : list_user_widgets,
        "name" : "User Widgets",
        "type" : "listview"
    },
    GPIB_INTF_ID : {
        "get" :  get_interface_setting,
        "set" : set_interface_setting,
        "options" : list_interface_options(),
        "default" : INTERFACE_DEFAULT,
        "type" : "selector",
        "name" : "Interface Type"
    },
    VISA_BACKEND_ID : {
        "get" : get_visa_backend_setting,
        "set" : set_visa_backend_settings,
        "default": VISA_BACKEND_DEFAULT,
        "options": ['@ni','@py'],
        "name": "VISA Backend",
        "type" : "selector"
    }
}

if __name__ == "__main__":
    pass
