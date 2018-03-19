# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 23:27:44 2013

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""
import logging 
import py_compile
from LabGuiExceptions import ScriptFile_Error
import sys 

from LabTools.IO import IOTool
import time
####
#import sys 
####
from LocalVars import USE_PYQT5

if  USE_PYQT5:
    
    from PyQt5.QtCore import QObject, Qt, QMutex, QThread, pyqtSignal
    
else:
    
    from PyQt4.QtCore import SIGNAL,QObject, Qt, QMutex, QThread


class DataTaker(QThread):
    """
        This object goal is to run the script from the configuration file. It
        can access all instrument in its instrument hub (see Drivers->Tool.py-->InstrumentHub)
        As it is child from QThread one can launch it using its inherited .start() method.
    """

    #creating signals
    if  USE_PYQT5:
        #emitted when the data array changes
        data = pyqtSignal('PyQt_PyObject')
        #emitted upon completion of the script
        script_finished = pyqtSignal(bool)

    def __init__(self, lock, instr_hub, parent=None):
        print("DTT created")
        super(DataTaker, self).__init__(parent)

        self.instr_hub = instr_hub
        
        if  USE_PYQT5:
            
            self.instr_hub.changed_list.connect(self.reset_lists)
        
        else:
            
            self.connect(self.instr_hub, SIGNAL(
                "changed_list()"), self.reset_lists)
            
            
        self.lock = lock
        self.stopped = True
        self.paused = False
        self.mutex = QMutex()

        self.completed = False
        self.DEBUG = IOTool.get_debug_setting()


        #the script which is run everytime the user call the routine "run"
        self.script_file_name = ''
        
        #a dict that can be populated by variable the user would like to change
        #in real time while the script is ran
        self.user_variables = {}        
        
        self.t_start = None
        # scriptize the intruments and their parameters
        self.reset_lists()

    def __del__(self):
        print("DTT deleted")

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

    def assign_user_variable(self, key, value_type = float, default = None):
        """this is used to change variables while data are being taken
        """
        
        #the key exists
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
                #assign the default value to the key entry
                self.user_variables[key] = default
                #make a recursive call to the method
                return self.assign_user_variable(key, value_type) 
                
    def run(self):
        print("DTT begin run\n")
        self.stopped = False
        # open another file which contains the script to follow for this
        # particular measurement
        userScriptName = self.script_file_name 
        try:
            logging.info("Opening script %s"%userScriptName)
            ext = userScriptName[userScriptName.index('.'):]
            if(ext != ".py"):
                raise(ScriptFile_Error("Incorrect filetype: %s"
                                       %(ext)))
            script = open(userScriptName)
            py_compile.compile(script.name, doraise=True)
            code = compile(script.read(), script.name, 'exec')
            exec(code)
            script.close()
            self.completed = True 
            print("DTT run over\n")
        except FileNotFoundError as fileNotFoundError:
            # script not found/script invalid 
            logging.error("Your script file \"%s\" "%(userScriptName) +
                              "failed to open with error:\n" + 
                              str(fileNotFoundError) + 
                              "\nPlease review the script.\n")
            raise(ScriptFile_Error(fileNotFoundError))
        except ScriptFile_Error as filetypeError: 
            logging.error("Your script file \"%s\" "%(userScriptName) +
                              "failed to open with error:\n" + 
                              str(filetypeError) + 
                              "\nPlease review the script.\n")
            raise(ScriptFile_Error(filetypeError))
        except py_compile.PyCompileError as compileError:
            logging.error("Your script file \"%s\" "%(userScriptName) +
                              "failed to compile with error:\n" + 
                              str(compileError) + 
                              "\nPlease review the script.\n")
            raise(ScriptFile_Error(compileError))
        except Exception as e: 
            logging.error("Your script file \"%s\" "%(userScriptName) +
                              "failed to run with error:\n" + 
                              type(e).__name__ + ": " + str(e) + 
                              "\nPlease review the script.\n")
        finally: 
            self.stop() 

    def set_script(self, script_fname):
        self.script_file_name = script_fname

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
            print("DTT stopped")
        finally:
            self.mutex.unlock()

    def pause(self):
        print("DTT paused")
        self.paused = True

    def resume(self):
        print("DTT resumed")
        self.paused = False

    def isPaused(self):
        return self.paused

    def isStopped(self):
        return self.stopped

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


class DataWriter(QObject):

    def __init__(self, datataker, debug=False, parent=None):
        super(DataWriter, self).__init__(parent)
        self.debug = debug
        
        if USE_PYQT5:
            
            datataker.data.connect(self.displayer, Qt.QueuedConnection)
            
        else:
            
            self.connect(datataker, SIGNAL("data(PyQt_PyObject)"),
                         self.writer, Qt.QueuedConnection)        

    def writer(self, data):

        #       print self.output_file_name
        #        self.out_file = open(self.output_file_name, 'a')
        #        self.log_file = open(self.output_file_name.rstrip('.dat') + ".log", 'a')
        #         self.log_file.write("%s %s %s\n\n"%(instr_type.center(w), dev.center(w), param.center(w)))
        #        self.log_file.write('Starting time: ' + str(self.t_start) + ' = ' + time.ctime() +'\n\n')
        #
        #        # print list of names to the terminal and to the file as headers
        #        stri = str(type_list).strip('[]')
        # print stri
        #        #print self.out_file.name
        #        self.out_file.write(stri + '\n')
        #
        #
        #        w = 15
        #        self.log_file.write("Instrument Configuration:\n\n")
        #        self.log_file.write("%s %s %s %s\n\n"%("Name".center(w),
        #                                               "Type".center(w), "Device".center(w), "Param".center(w)))

        #                self.out_file.close()
        #        self.log_file.close()

        if not self.debug:

            stri = str(data).strip('[]\n\r')
            # numpy arrays include newlines in their strings, get rid of them.
#            stri = stri.replace(' ', '\t')
            # print exactly the string which is going to be written in the file
            print('>>>>' + stri)

        else:
            print("writer triggered")
