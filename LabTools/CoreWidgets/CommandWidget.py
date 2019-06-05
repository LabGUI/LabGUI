# -*- coding: utf-8 -*-
"""
Created on May 28 2019

@author: zackorenberg

A GPIB commandline widget
"""

# -*- coding: utf-8 -*-
"""
Created for GervaisLabs
"""

import sys

from types import MethodType
import logging

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui

else:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore

from LabTools.Display import QtTools

import sys
import io
import inspect
import matplotlib.pyplot as plt
import shlex

class CommandWidget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features"""

    def __init__(self, parent=None):
        super(CommandWidget, self).__init__()

        self.DEBUG = False
        self.INFO = True #returns callback and trace for general errors in console

        #aesthetic stuff
        self.setWindowTitle("GPIB Command-Line")
        self.resize(500,250)


        #command line
        self.commandLineEdit = QtGui.QLineEdit()

        #self.commandLineEdit.editingFinished.connect(self.enterPress)
        self.commandLineEdit.returnPressed.connect(self.enterPress)
        self.commandLineEdit.textChanged.connect(self.textChanged)
        self.commandLineEdit.setPlaceholderText("Please enter a command")

        #device dropdown
        self.deviceComboBox = QtGui.QComboBox()
        self.deviceComboBox.activated[str].connect(self.change_device)
        #self.deviceComboBox.s

        self.currentDevice = None

        if self.DEBUG is True:
            self.deviceComboBox.addItem("Test 1", 1)
            self.deviceComboBox.addItem("Test 2", 2)
            self.deviceComboBox.addItem("Test 3", 3)

        #output console
        self.consoleTextEdit = QtGui.QTextEdit()

        self.consoleTextEdit.setReadOnly(True)

        self.verticalLayout = QtGui.QVBoxLayout()

        self.verticalLayout.addWidget(self.commandLineEdit)
        self.verticalLayout.addWidget(self.deviceComboBox)
        self.verticalLayout.addWidget(self.consoleTextEdit)

        self.setLayout(self.verticalLayout)

        self.console_text("Please enter GPIB command")

        self.instrument_list = {}
        self.sanitized_list = list() # tuple, (name, port, object)

        self.history = list()

        self.numbers = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

        self.vars = ['history', 'INFO', 'numbers']

        if parent is not None:
            self.parentClass = parent
            self.instr_hub = parent.instr_hub
        else:
            self.parentClass = None
            self.instr_hub = None
        #elif self.parentClass is None:
        #    self.instr_hub = None


    # create focus in override to refresh devices
    def enterEvent(self, event):
        #using this enterEvent until I find a more effective way
        self.update_devices()
        #return super(CommandWidget, self).enternEvent(event)
    def console_text(self, new_text=None):
        """get/set method for the text in the console"""

        if new_text is None:

            return str((self.consoleTextEdit.toPlainText())).rstrip()

        else:

            self.consoleTextEdit.setPlainText(new_text)

    def enterPress(self):
        cmd = self.commandLineEdit.text()
        #print("Text: "+cmd)
        self.execute_command(cmd)
        #self.update_console(cmd)
        #self.commandLineEdit.clear()


    def textChanged(self, text):
        #print(text)
        return



    def execute_command(self, cmd):
        if cmd in '': #default for empty string, returns as to not cause error and crash
            return

        self.history.append(cmd)
        strl = cmd.split(' ', 1)
        if len(strl) is 0:
            action = None #will cause incorrect command to write
        else:
            action = strl[0].lower()
        if len(strl) is 2:
            command = strl[1]
        else:
            command = None

        #find current device
        if action in "refresh":
            self.update_devices()
            self.commandLineEdit.clear()
            return
        current_device = self.deviceComboBox.currentIndex()
        if current_device is -1:
            self.update_console("Please connect to a device before executing a command, or refresh device list by typing 'refresh'")
        #print(current_device)
        if action.lower() == "query" or action.lower() == "ask":
            resp = "None"
            try:
                resp = self.sanitized_list[current_device][2].ask(command)
            except:
                resp = "Something went wrong"
                pass
            self.update_console(command+": "+resp)
        elif action.lower() == "write":
            resp = "Written"
            try:
                self.sanitized_list[current_device][2].write(command)
            except:
                resp = "Something went wrong"
                pass
            self.update_console(command + ": " + resp)
        elif action.lower() == "read":
            try:
                resp = self.sanitized_list[current_device][2].read()
            except:
                resp = "Something went wrong"
                pass
            self.update_console("read: " + resp)
        elif "funct" in action.lower() or action.lower() == "run":
            #run custom function inside driver
            # split funct and params
            try:
                funct, params = command.split(' ', 1)
            except (ValueError, IndexError, TypeError): #no params
                funct = command
                params = None
                pass
            #split params
            try:
                params = params.split(' ')
            except (ValueError, IndexError, TypeError): #1 param
                params = [params]
                pass
            except:
                params = []
                pass

            #now actually call the command
            try:
                resp = getattr(self.sanitized_list[current_device][2], funct)(*params)
                self.update_console("Function returned with: "+self.print_to_string(resp))
            except AttributeError: #errors likely caused by run syntax
                self.update_console(self.print_to_string("Failed to run command: Attribute Error. Likely invalid function name or command syntax"))
                self.update_console(self.print_to_string("Use 'methods' to obtain list of callable functions"))
                self.update_console(self.print_to_string("Use 'run function paramater1 parameter2 etc' to execute function"))
                if self.INFO:
                    self.update_console(self.print_to_string(sys.exc_info()))
                pass
            except: #any other errors
                self.update_console(self.print_to_string("Failed to run command: ",sys.exc_info()[0]))
                if self.INFO:
                    self.update_console(self.print_to_string(sys.exc_info()))
                pass
        elif action.lower() == "plot":
            # generally going to be the same as methods, but will initialize matplotlib plot
            try:
                funct, params = command.split(' ', 1)
            except (ValueError, IndexError, TypeError): #no params
                funct = command
                params = None
                pass
            #split params
            try:
                params = params.split(' ')
            except (ValueError, IndexError, TypeError): #1 param
                params = [params]
                pass
            except:
                params = []
                pass

            #now actually call the command
            try:
                resp = getattr(self.sanitized_list[current_device][2], funct)(*params)
            except AttributeError: #errors likely caused by run syntax
                self.update_console(self.print_to_string("Failed to run command: Attribute Error. Likely invalid function name or command syntax"))
                self.update_console(self.print_to_string("Use 'methods' to obtain list of callable functions"))
                self.update_console(self.print_to_string("Use 'run function paramater1 parameter2 etc' to execute function"))
                if self.INFO:
                    self.update_console(self.print_to_string(sys.exc_info()))
                return
            except: #any other errors
                self.update_console(self.print_to_string("Failed to run command: ",sys.exc_info()[0]))
                if self.INFO:
                    self.update_console(self.print_to_string(sys.exc_info()))
                return
            if type(resp) == list:
                try:
                    axes = list(zip(*resp))
                except:
                    self.update_console("Invalid return data:")
                    self.update_console(self.print_to_string(resp))
                    if self.INFO:
                        self.update_console(self.print_to_string(sys.exc_info()))
                    return

                n = len(axes) # number of axis

                combos = [ list(range(i+1, n)) for i in range(0, n-1) ]

                # now do it for every combination
                for i in range(0, n-1):
                    plt.figure(i+1)
                    k = 0
                    for j in combos[i]:
                        plt.subplot(n-1-i, 1, k+1)
                        plt.plot(axes[i], axes[j])
                        if len(self.numbers) >= n:
                            plt.xlabel(self.numbers[i])
                            plt.ylabel(self.numbers[j])
                        k+=1

                plt.show()

                #plt.plot(x,y)
            else:
                self.update_console("Invalid return data:")
                self.update_console(self.print_to_string(resp))
        elif "methods" == action.lower():
            object_methods = [method_name
                              for method_name in dir(self.sanitized_list[current_device][2])
                              if callable(getattr(self.sanitized_list[current_device][2], method_name))]
            methods_and_sigs = []
            for method in object_methods:
                try:
                    if(callable(getattr(self.sanitized_list[current_device][2], method))):
                        sig = inspect.signature(getattr(self.sanitized_list[current_device][2], method))
                        if not method.startswith("__") and not method.endswith("__"):
                            methods_and_sigs.append((method, str(sig)))
                except:
                    #this means that method isnt actually callable or that inspect.signature throws error
                    pass
            #for i in range(0, len(object_methods)):
            #    if object_methods[i][:2] == "__":
            #        object_methods.pop(i)
            self.update_console(self.print_to_string("===" + self.sanitized_list[current_device][0] + "==="))
            self.update_console(self.print_to_string("Callable functions: ", len(methods_and_sigs)))
            for tup in methods_and_sigs:
                self.update_console("\t"+tup[0]+tup[1])
            #object_sig = [
            #    inspect.signature(getattr(self.sanitized_list[current_device][2], method_name))
            #    for method_name in dir(self.sanitized_list[current_device][2])
            #    if callable(getattr(self.sanitized_list[current_device][2], method_name))]
            #print(object_sig)
            # it aint pretty, but it gets the job done
        elif action.lower() == "set": # to set command line variables
            try:
                var, params = command.split(" ", 1)
            except: # at most one word in command
                var = command
                params = None
                pass

            if var is None:
                # print list of variables setable
                try:
                    self.update_console(self.print_to_string(self.vars))
                except:
                    self.update_console(self.print_to_string("An error occurred: ", sys.exc_info()[0]))
                    if self.INFO:
                        self.update_console(self.print_to_string(sys.exc_info()))
                    pass
            elif params is None:
                # read value of var
                try:
                    self.update_console(self.print_to_string(self.read_vars(var)))
                except:
                    self.update_console(self.print_to_string("An error occurred: ", sys.exc_info()[0]))
                    if self.INFO:
                        self.update_console(self.print_to_string(sys.exc_info()))
                    pass
            else:
                try:
                    self.update_console(self.print_to_string(self.set_vars(var, params)))
                except:
                    self.update_console(self.print_to_string("An error occurred: ", sys.exc_info()[0]))
                    if self.INFO:
                        self.update_console(self.print_to_string(sys.exc_info()))
                    pass

        elif action.lower() == "help":
            # write help stuff here
            if command is None:
                self.update_console("Usage: help <command>")
                self.update_console("=== Commands ===")
                self.update_console("\tread\n\twrite <cmd>\n\tquery/ask <cmd>\n\tmethods\n\trun <funct> <parameters>\n\tclear\n\tplot <funct> <parameters>\n\tset <variable> <parameters>")
            elif command.lower() == "read":
                text = [
                    "Usage: " + command.lower(),
                    "read:\treads from device",
                    "Will only return data if there is something to read off the machines buffer, otherwise it'll return an error"
                ]
                for i in text:
                    self.update_console(i)
            elif command.lower() == "write":
                text = [
                    "Usage: " + command.lower(),
                    "query/ask <cmd>:\tqueries device",
                    "<cmd> must be a valid GPIB command readible by the connected machine",
                    "Do not enclose your entire <cmd> with quotation marks",
                    "Note: 'Written' will always return on success"
                ]
                for i in text:
                    self.update_console(i)
            elif command.lower() == "query" or command.lower() == "ask":
                text = [
                    "Usage: " + command.lower(),
                    "query/ask <cmd>:\tqueries device",
                    "<cmd> must be a valid GPIB command readible by the connected machine",
                    "Do not enclose your entire <cmd> with quotation marks"
                ]
                for i in text:
                    self.update_console(i)
            elif command.lower() == "methods":
                self.update_console("Usage: " + command.lower())
                self.update_console("methods:\treturns list of callable functions and parameters")
            elif command.lower() == "run":
                text = [
                    "Usage: " + command.lower(),
                    "run <funct> <parameters>:\truns callable function",
                    "valid functions for <funct> are given by methods command",
                    "all <parameters> must be seperated by spaces"
                ]
                for i in text:
                    self.update_console(i)
            elif command.lower() == "clear":
                self.update_console("Usage: " + command.lower())
                self.update_console("clear:\tclears console window")
            elif command.lower() == "plot":
                text = [
                    "Usage: " + command.lower(),
                    "plot <funct> <parameters>:\tplots return of callable function",
                    "valid functions for <funct> are given by methods command",
                    "all <parameters> must be seperated by spaces",
                    "Please note, only functions that return a list of plotable coordinates of any dimension will plot",
                    "Axis names can be set via 'set numbers' command, where the first array entry corresponds to the first coordinate, second entry to the second coordinate, etc"
                ]
                for i in text:
                    self.update_console(i)
            elif command.lower() == "set":
                text = [
                    "Usage: " + command.lower(),
                    "set <variable> <parameters>:\tsets/gets environment variable of this command-line",
                    "the only invalid variable names are the names of callable functions",
                    "example usage:",
                    "\tset",
                    "returns list of all environment variables",
                    "\tset varname",
                    "returns value of environment variable 'varname'",
                    "\tset varname foo",
                    "sets value of environment variable 'varname' to the string 'foo'"
                    "\tset varname foo bar",
                    "sets value of environment variable 'varname' to list containing entries 'foo' and 'bar' at position 0 and 1 respectively",
                    "\tset varname 0=bar",
                    "sets value of environment variable 'varname' at position 0 to the string 'bar', resulting in ['bar', 'bar']",
                    "\tset varname 'foo bar'",
                    "sets value of environment variable 'varname' to the string 'foo bar'",
                    "=== Some important variables ===",
                    "\tnumbers : contains axes information for 'plot'",
                    "\tINFO : Boolean variable that prints extra information regarding errors when set to True"
                ]
                for i in text:
                    self.update_console(i)
            else:
                self.update_console("Invalid command: "+command)

        else:
            self.update_console("Command must start with 'query', 'write', or 'read'")
            return

        #if this point was reached, the command is valid, so execute and clear
        self.commandLineEdit.clear()

    def automatic_scroll(self):
        """performs an automatic scroll up

        the latest text shall always be in view
        """
        sb = self.consoleTextEdit.verticalScrollBar()
        sb.setValue(sb.maximum())


    def change_device(self, text):
        id = self.deviceComboBox.findText(text)

        #turns out this is not needed, as on every command it gets current device


        # to remove item self.deviceComboBox.removeItem(id)

    def update_instrument_list(self):
        if self.parentClass is not None:
            self.instrument_list = self.parentClass.instr_hub.get_instrument_list()
            #print(self.instrument_list)

            #print(self.parentClass.instr_hub.get_port_param_pairs())
            #print(self.parentClass.instr_hub.get_instrument_nb())

            z = self.instrument_list.items()

            ports = list()
            instruments = list()
            names = list()
            for x, y in z:
                if x is not None and "ComputerTime" not in x:
                    ports.append(x)
                    instruments.append(self.instrument_list[x])
                    names.append(self.instrument_list[x].ID_name)
                    #print(x,self.instrument_list[x].ID_name)
            self.sanitized_list = list(zip(names, ports, instruments))
            return

    def update_devices(self):
        # going need to get get_instrument_list
        self.update_instrument_list()
        text = self.deviceComboBox.currentText() # to set back to
        self.deviceComboBox.clear()
        for tuples in self.sanitized_list:
            self.deviceComboBox.addItem(tuples[0]+" on "+tuples[1])
        # now time to set current choice if it is still in the list
        index = self.deviceComboBox.findText(text)
        if index != -1:
            self.deviceComboBox.setCurrentIndex(index)
        # now it should work perfectly with multiple devices

    def read_vars(self, var):
        if var not in self.vars:
            return "Variable does not exist"
        else:
            return getattr(self, var)


    def set_vars(self, var, data): #assume vars are all strings, except INFO
        if data is None: # shouldnt happen, but just in case
            return False
        dat = [var] + shlex.split(data) #fix for code i wrote
        if dat[0] not in self.vars:
            if hasattr(self, dat[0]):
                return "Cannot set variable, reserved in class"
                # likely just trying to set var
            else: # make variable
                information = dat[1::]
                if len(information) == 1:
                    setattr(self, dat[0], information[0]) # dont save single string as list
                else:
                    setattr(self, dat[0], information) #save extra data as list
            # now save in self.vars so it doesnt rewrite every time
            self.vars.append(dat[0])
            return (dat[0], getattr(self, dat[0])) # tuple, first is name, second is value
        elif dat[0] == 'INFO': # specific case for type casting
            if dat[1] == 'True' or det[1] == '1':
                self.INFO = True
                return "INFO set to True"
            elif dat[1] == 'False' or det[1] == '0':
                self.INFO = False
                return "INFO set to False"
            else:
                return "Invalid option. INFO can only be True or False"
        else: # modify current var
            information = dat[1::]
            if len(information) > 1: #clearly an array is to be set
                #maybe implement = thing
                setattr(self, dat[0], information)
                return (dat[0], getattr(self, dat[0]))
            else: # part as string
                stri = information[0]
                escaped_list = shlex.shlex(stri)
                escaped_list.whitespace += '='
                escaped_list.whitespace_split = True
                strlist = list(escaped_list)
                if len(strlist) == 1: #no equal sign
                    setattr(self, dat[0], strlist[0])
                elif len(strlist) == 2: #one setting another
                    if strlist[0].isdigit():
                        getattr(self, dat[0])[int(strlist[0])] = strlist[1]
                    else: # will throw error if data is not object!!!
                        getattr(self, dat[0])[strlist[0]] = strlist[1]
                elif len(strlist) > 2: # shouldnt reach here, unless if len(information) is changed
                    if strlist[0].isdigit():
                        getattr(self, dat[0])[int(strlist[0])] = strlist[1::]
                    else:  # will throw error if data is not object!!!
                        getattr(self, dat[0])[strlist[0]] = strlist[1::]
                else:
                    return "An error occured if you reached here."
                return (dat[0], getattr(self, dat[0]))




    def print_to_string(self, *args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents

    def update_console(self, stri):
        # based on update_console code for consolewidget
        MAX_LINES = 50

        stri = str(stri) # to make sure it is infact a string

        new_text = self.console_text() + '\n' + stri

        line_list = new_text.splitlines()
        N_lines = min(MAX_LINES, len(line_list))

        new_text = '\n'.join(line_list[-N_lines:])

        self.console_text(new_text)

        self.automatic_scroll()

    def clear_console(self):
        self.consoleTextEdit.clear()


def add_widget_into_main(parent):
    return #we dont want this to happen yet
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = ConsoleWidget(parent=parent)

    # create a QDockWidget
    consoleDockWidget = QtGui.QDockWidget("Output Console", parent)
    consoleDockWidget.setObjectName("consoleDockWidget")
    consoleDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        | QtCore.Qt.BottomDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['ConsoleWidget'] = mywidget

    consoleDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, consoleDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(consoleDockWidget.toggleViewAction())

    # redirect print statements to show a copy on "console"
    sys.stdout = QtTools.printerceptor(parent)

    # assigning a method to the parent class
    # depending on the python version this fonction take different arguments
    if sys.version_info[0] > 2:

        parent.update_console = MethodType(update_console, parent)

    else:

        parent.update_console = MethodType(
            update_console, parent, parent.__class__)

    if USE_PYQT5:

        sys.stdout.print_to_console.connect(parent.update_console)

    else:

        parent.connect(sys.stdout, QtCore.SIGNAL(
            "print_to_console(PyQt_PyObject)"), parent.update_console)


"""def update_console(parent, stri):

    MAX_LINES = 50

    stri = str(stri)
    new_text = parent.widgets['ConsoleWidget'].console_text() + '\n' + stri

    line_list = new_text.splitlines()
    N_lines = min(MAX_LINES, len(line_list))

    new_text = '\n'.join(line_list[-N_lines:])

    parent.widgets['ConsoleWidget'].console_text(new_text)

    parent.widgets['ConsoleWidget'].automatic_scroll()
"""

if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    ex = CommandWidget()
    ex.show()
    sys.exit(app.exec_())
