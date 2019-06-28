# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 23:27:44 2013

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""
import logging
import py_compile
import time
import os

from LabGuiExceptions import ScriptFile_Error
from LabTools.IO import IOTool

####
#import sys
####
from LocalVars import USE_PYQT5

if USE_PYQT5:

    from PyQt5.QtCore import QObject, Qt, QMutex, QThread, pyqtSignal

else:

    from PyQt4.QtCore import SIGNAL, QObject, Qt, QMutex, QThread


class DataTaker(QThread):
    """
        This object goal is to run the script from the configuration file. It
        can access all instrument in its instrument hub (see Drivers->Tool.py-->InstrumentHub)
        As it is child from QThread one can launch it using its inherited .start() method.
    """

    # creating signals
    if USE_PYQT5:
        # emitted when the data array changes
        data = pyqtSignal('PyQt_PyObject')
        # emitted upon completion of the script
        script_finished = pyqtSignal(bool)

    def __init__(self, lock, instr_hub, parent=None):
        logging.debug("DTT created")
        super(DataTaker, self).__init__(parent)

        self.instr_hub = instr_hub

        if USE_PYQT5:

            self.instr_hub.changed_list.connect(self.reset_lists)

        else:

            self.connect(self.instr_hub, SIGNAL(
                "changed_list()"), self.reset_lists)

        self.lock = lock

        self.running = False

        self.stopped = True

        self.paused = False

        self.mutex = QMutex()

        self.completed = False

        self.DEBUG = IOTool.get_debug_setting()

        # the script which is run everytime the user call the routine "run"
        self.script_file_name = ''

        # a dict that can be populated by variable the user would like to change
        # in real time while the script is ran
        self.user_variables = {}

        self.t_start = None
        # scriptize the intruments and their parameters
        self.reset_lists()

    def initialize(self, first_time=False):
        self.stopped = False

        if first_time:
            for key, inst in list(self.instruments.items()):
                # there's a none object in the Instruments list, ignore it
                if inst:
                    inst.initialize()

    def reset_lists(self):
        """
            If changes are made to the InstrumentHub, the DataTaker will not acknowledge them
            unless using this method
        """
       # print("\tChange instruments in datataker...")
        self.instruments = self.instr_hub.get_instrument_list()
        self.port_param_pairs = self.instr_hub.get_port_param_pairs()
        #print("\t...instruments updated in datataker")

    def update_user_variables(self, adict):
        """
        Replace the user variables by updated ones
        """

        if isinstance(adict, dict):

            self.user_variables = adict

    def assign_user_variable(self, key, value_type=float, default=None):
        """this is used to change variables while data are being taken
        """

        # the key exists
        if key in self.user_variables:

            if value_type == None:

                return self.user_variables[key]

            else:

                if isinstance(value_type, type):

                    try:

                        return value_type(self.user_variables[key])

                    except ValueError:
                        print("Wrong type conversion applied on \
user variable")
                        return self.user_variables[key]

                else:

                    print("Wrong type used for user variable")
                    return self.user_variables[key]

        else:

            if default == None:

                print("The user variable key %s isn't defined" % key)

            else:
                # assign the default value to the key entry
                self.user_variables[key] = default
                # make a recursive call to the method
                return self.assign_user_variable(key, value_type)

    def run(self):

        rel_path = os.path.basename(os.path.abspath(os.path.curdir))
        rel_path = self.script_file_name.split(rel_path)[1]


        print("\nDTT begin run: '.%s'\n" % (rel_path))
        self.stopped = False
        self.running = True
        self.paused = False
        # open another file which contains the script to follow for this
        # particular measurement
        userScriptName = self.script_file_name
        try:
            ext = userScriptName[userScriptName.index('.'):]
            if(ext != ".py"):
                raise(ScriptFile_Error("Incorrect filetype: %s"
                                       % (ext)))
            script = open(userScriptName)
            py_compile.compile(script.name, doraise=True)
            code = compile(script.read(), script.name, 'exec')

            exec(code)
            script.close()

            self.running = False
            self.paused = False
            self.completed = True
            print("\nDTT run over\n")

        except FileNotFoundError as fileNotFoundError:
            # script not found/script invalid
            logging.error("Your script file \"%s\" " % (userScriptName) +
                          "failed to open with error:\n" +
                          str(fileNotFoundError) +
                          "\nPlease review the script.\n")
            raise(ScriptFile_Error(fileNotFoundError))
        except ScriptFile_Error as filetypeError:
            logging.error("Your script file \"%s\" " % (userScriptName) +
                          "failed to open with error:\n" +
                          str(filetypeError) +
                          "\nPlease review the script.\n")
            raise(ScriptFile_Error(filetypeError))
        except py_compile.PyCompileError as compileError:
            logging.error("Your script file \"%s\" " % (userScriptName) +
                          "failed to compile with error:\n" +
                          str(compileError) +
                          "\nPlease review the script.\n")
            raise(ScriptFile_Error(compileError))
        except Exception as e:
            logging.error("Your script file \"%s\" " % (userScriptName) +
                          "failed to run with error:\n" +
                          type(e).__name__ + ": " + str(e) +
                          "\nPlease review the script.\n")
        finally:
            pass
        # send a signal to indicate that the DTT is stopped
        if USE_PYQT5:

            self.script_finished.emit(self.completed)

        else:

            self.emit(SIGNAL("script_finished(bool)"), self.completed)
        self.stop()

    def set_script(self, script_fname):
        self.script_file_name = os.path.abspath(script_fname) # FIX TO ALLOW RELATIVE PATHS

    def stop(self):

        try:

            self.mutex.lock()
            self.stopped = True

            self.running = False

            if self.completed:
                print("DTT stopped and complete")
            else:
                print("DTT stopped but not complete")

        finally:

            self.mutex.unlock()

    def pause(self):
        print("DTT paused")
        self.paused = True

    def resume(self):
        print("DTT resumed")
        self.paused = False

    def isRunning(self):

        return self.running

    def isPaused(self):

        return self.paused

    def isStopped(self):

        return self.stopped

    def ask_to_stop(self):

        self.stopped = True
        self.paused = False

    def check_stopped_or_paused(self):

        while True:

            if (not self.paused) or self.stopped:

                return self.stopped

            time.sleep(0.1)

    def read_data(self):
        """
            Call the method "measure" for each instrument in InstrumentHub.
            It collect the different values of corresponding parameters and
            emit a signal which will be catch by other instance for further
            treatment.
        """
#        param_set = []
        data_set = []

        for port, param in self.port_param_pairs:
            inst = self.instruments[port]

            if inst != '' and inst != None:
                #            if inst !='TIME' and inst!='' and inst!= None:
                data_set.append(inst.measure(param))
#                param_set.append(inst.channels_names[param])
#            elif inst =='TIME':
#                data_set.append(round(t_meas,2))
#                param_set.append('TIME')
            else:
                data_set.append(0)
#                param_set.append('')

        # send data back to the mother ship as an array of floats, but only
        if USE_PYQT5:

            self.data.emit(data_set)

        else:

            self.emit(SIGNAL("data(PyQt_PyObject)"), data_set)


class DataDisplayer(QObject):

    def __init__(self, datataker, debug=False, parent=None):
        super(DataDisplayer, self).__init__(parent)
        self.debug = debug
#        self.lock = lock
        if USE_PYQT5:

            datataker.data.connect(self.displayer, Qt.QueuedConnection)

        else:

            self.connect(datataker, SIGNAL("data(PyQt_PyObject)"),
                         self.displayer, Qt.QueuedConnection)

    def displayer(self, data):

        # can do different things depending on the window type which is active

        if not self.debug:

            stri = str(data).strip('[]\n\r')
            # numpy arrays include newlines in their strings, get rid of them.
            stri = stri.replace(', ', ' ')
            # print exactly the string which is going to be written in the file
            # print '>>' + stri

        else:
            print("displayer triggered")

