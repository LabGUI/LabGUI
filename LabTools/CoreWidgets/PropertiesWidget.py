# -*- coding: utf-8 -*-
"""
Created on Jun 7 2019

@author: zackorenberg

A widget designed to read/write properties to machine. Not working YET
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

from collections import Iterable

import sys
import io
import inspect
import matplotlib.pyplot as plt
import shlex

class PropertiesWidget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features"""

    def __init__(self, parent=None):
        super(PropertiesWidget, self).__init__()

        self.DEBUG = False

        #aesthetic stuff
        self.setWindowTitle("Device Properties")
        self.resize(500,250)


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

        self.verticalLayout.addWidget(self.deviceComboBox)

        self.setLayout(self.verticalLayout)

        self.console_text("Please enter GPIB command")

        self.instrument_list = {}
        self.sanitized_list = list() # tuple, (name, port, object)


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




    def print_to_string(self, *args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents

    def iterable_to_str(self, o):
        try:
            return " ".join([str(i) for i in o])
        except:
            self.update_console(self.print_to_string("Unable to join object", sys.exc_info()[0]))
            if self.INFO:
                self.update_console(self.print_to_string(sys.exc_info()))
            return o



# def toggleViewAction(dock_widget, docked=True):
#     if docked:
#         dock_widget.toggleViewAction()
#     else:
#         dock_widget.widget().show()

def add_widget_into_main(parent):
    return #we dont want this to happen yet
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = PropertiesWidget()

    # create a QDockWidget
    propDockWidget = QtGui.QDockWidget("Device Properties", parent)
    propDockWidget.setObjectName("propertiesDockWidget")
    propDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        | QtCore.Qt.BottomDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['PropertiesWidget'] = mywidget

    propDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, propDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(propDockWidget.toggleViewAction())

    # redirect print statements to show a copy on "console"
    sys.stdout = QtTools.printerceptor(parent)

    propDockWidget.resize(500,250)
    propDockWidget.hide()



    # assigning a method to the parent class
    # depending on the python version this fonction take different arguments
    # if sys.version_info[0] > 2:
    #
    #     parent.update_console = MethodType(update_console, parent)
    #
    # else:
    #
    #     parent.update_console = MethodType(
    #         update_console, parent, parent.__class__)

    # if USE_PYQT5:
    #
    #     sys.stdout.print_to_console.connect(parent.update_console)
    #
    # else:
    #
    #     parent.connect(sys.stdout, QtCore.SIGNAL(
    #         "print_to_console(PyQt_PyObject)"), parent.update_console)


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

# def add_widget_into_main(parent):
#     """add a widget into the main window of LabGuiMain
#
#     create a QDock widget and store a reference to the widget
#     """
#
#     mywidget = CommandWidget(parent=parent)
#
#     outDockWidget = QtGui.QDockWidget("GPIB Command-Line", parent)
#     outDockWidget.setObjectName("OutputFileDockWidget")
#     outDockWidget.setAllowedAreas(
#         Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
#
#     # fill the dictionnary with the widgets added into LabGuiMain
#     parent.widgets['CommandWidget'] = mywidget
#
#     outDockWidget.setWidget(mywidget)
#     parent.addDockWidget(Qt.RightDockWidgetArea, outDockWidget)
#
#     # Enable the toggle view action
#     parent.windowMenu.addAction(outDockWidget.toggleViewAction())

if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    ex = CommandWidget()
    ex.show()
    sys.exit(app.exec_())
