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

import LabDrivers.utils

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui
    import PyQt5.QtGui as Qt

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
import time

DEBUG = False

class DevicePropertyWidget(QtGui.QWidget):

    def __init__(self, device, property_obj, parent=None, debug=False):
        super(DevicePropertyWidget, self).__init__(parent=parent)

        self.DEBUG = debug

        self.device = device
        if self.DEBUG:
            self.properties = {
                'Selection box': {
                    'type':'selection',
                    'range':[
                        'option',
                        'another option',
                        'a third option',
                        'unsurprisingly, a fourth option'
                    ]
                },
                'Float only': {
                    'type':'float',
                    'range':[-100, 100]
                },
                'Int only': {
                    'type':'int',
                    'range':[-100, 100]
                },
                'Boolean type':{
                    'type':'bool',
                    'range':True
                },
                'Text type':{
                    'type':'text',
                    'range':'Placeholder'
                }
            }
        else:
            self.properties = property_obj

        self.layout = QtGui.QFormLayout(self)
        self.prop_items = {}

        if self.device == None:
            self.layout = QtGui.QVBoxLayout(self)
            label = QtGui.QLabel(self)
            label.setText("No device selected")
            label.adjustSize()
            self.layout.addWidget(label)
        elif self.device == "NotExist":
            self.layout = QtGui.QVBoxLayout(self)
            label = QtGui.QLabel(self)
            label.setText("Selected device has no editable properties")
            label.adjustSize()
            label.setWordWrap(True)
            self.layout.addWidget(label)
        else:
            for item, iobj in self.properties.items():
                # print(item, iobj)
                label = item
                if 'unit' in iobj.keys():
                    label = item+"("+iobj['unit']+")"
                text = self.create_label(label)
                if iobj['type'] == 'selection':
                    qtobject = self.create_selector(item, iobj['range'])
                elif iobj['type'] == 'float':
                    qtobject = self.create_float(item, iobj['range'])
                elif iobj['type'] == 'int':
                    qtobject = self.create_int(item, iobj['range'])
                elif iobj['type'] == 'bool':
                    qtobject = self.create_bool(item, iobj['range'])
                elif iobj['type'] == 'text':
                    qtobject = self.create_text(item, iobj['range'])
                else:
                    qtobject = None
                    print("uh oh")
                self.prop_items[item] = qtobject
                if qtobject:
                    self.layout.addRow(text, qtobject)

        self.setLayout(self.layout)

    def get_properties(self): # return properties to be set by another class
        ret = {}
        #print(self.prop_items)
        for name, obj in self.prop_items.items():
            ret[name] = self.extract_property(obj)
            #print(obj.objectName())
        return ret

    def set_properties(self, data): # set properties with values provided by another class
        for name, obj in self.prop_items.items():
            if name in data.keys(): # this means it is valid property
                self.write_property(data[name], obj)
                print("working")


    def write_property(self, data, qtobject): #individual set type stuff
        typ = type(qtobject)
        if typ == QtGui.QComboBox:
            qtobject.setCurrentText(str(data))
        elif typ == QtGui.QLineEdit:
            qtobject.setText(str(data))
        elif typ == QtGui.QCheckBox:
            if data:
                qtobject.setChecked(True)
            else:
                qtobject.setChecked(False)
        else:
            print("Unknown type for ",data,": ", typ)
        return qtobject # add any other types to the if statement

    def extract_property(self, qtobject): # individual get type stuff
        # make this check the type, and return a value based on that
        typ = type(qtobject)
        if typ == QtGui.QComboBox:
            return qtobject.currentText()
        elif typ == QtGui.QLineEdit:
            return qtobject.text()
        elif typ == QtGui.QCheckBox:
            return qtobject.isChecked()
        else:
            return "unknown type"
        #return qtobject # If any other options are required, add em to if statement


    def change_setting(self, *args):
        print(args)

    def create_selector(self, name, items):
        ret = QtGui.QComboBox()
        ret.addItems(items)
        ret.setObjectName(name)
        ret.activated[str].connect(self.change_setting)
        return ret

    def create_float(self, name, range):
        ret = QtGui.QLineEdit()
        float_validator = Qt.QDoubleValidator(range[0], range[1], 6, ret)
        ret.setObjectName(name)
        ret.setValidator(float_validator)
        return ret

    def create_int(self, name, range):
        ret = QtGui.QLineEdit()
        ret.setObjectName(name)
        float_validator = Qt.QIntValidator(range[0], range[1])
        ret.setValidator(float_validator)
        return ret

    def create_text(self, name, range):
        ret = QtGui.QLineEdit()
        ret.setObjectName(name)
        if type(range) == str: #placeholder text
            ret.setPlaceholderText(range)
        return ret

    def create_bool(self, name, range):
        ret = QtGui.QCheckBox()
        ret.setObjectName(name)
        if type(range) == bool:
            ret.setChecked(range)
        return ret

    def create_label(self, text):
        ret = QtGui.QLabel(text)
        return ret




class PropertiesWidget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features ;)"""

    def __init__(self, parent=None, debug=False):
        super(PropertiesWidget, self).__init__()

        #self.DEBUG = debug
        if DEBUG:
            self.DEBUG = True
        else:
            self.DEBUG = debug
        self.properties = LabDrivers.utils.list_properties()
        self.device_layouts = {}
        self.layouts = {}

        self.stacked = QtGui.QStackedWidget(self)
        # populate stacked widget
        self.addDevices()
        # set current device
        if self.DEBUG:
            self.currentDevice = 'NotExist' # can change to any testing device
        else:
            self.currentDevice = None
        self.stacked.setCurrentWidget(self.widgets[self.currentDevice])
        #aesthetic stuff
        self.setWindowTitle("Device Properties")
        self.resize(500,250)



        #device dropdown
        self.deviceComboBox = QtGui.QComboBox()
        self.deviceComboBox.activated[str].connect(self.change_device)
        #self.deviceComboBox.s


        if self.DEBUG is True:
            print("Debug")

        #output console
        self.verticalLayout = QtGui.QVBoxLayout()

        self.verticalLayout.addWidget(self.deviceComboBox)
        self.verticalLayout.addStretch()
        self.verticalLayout.addWidget(self.stacked)
        self.verticalLayout.addStretch()
        self.footer = self.create_footer()
        self.verticalLayout.addLayout(self.footer)

        self.setLayout(self.verticalLayout)

        #self.console_text("Please enter GPIB command")

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



    # Floored till next commit
    #def create_layouts(self):
    #    print("should probably delete")
        # self.prop_items = {}
        # for name, obj in self.properties.items():
        #     print(name, obj)
        #     self.layouts[name] = QtGui.QFormLayout()
        #     self.prop_items[name] = {}
        #     for item, iobj in obj.items():
        #         print(item, iobj)
        #         text = self.create_label(item)
        #         if iobj['type'] == 'selection':
        #             qtobject = self.create_selector(item, iobj['range'])
        #         elif iobj['type'] == 'float':
        #             qtobject = self.create_float(item, iobj['range'])
        #         else:
        #             qtobject = None
        #             print("uh oh")
        #         self.prop_items[name][item] = qtobject
        #         if qtobject:
        #             self.layouts[name].addRow(text, qtobject)

    def addDevices(self):
        # creates widgets for all drivers with properties, regardless of connection
        objs = {}
        for name, obj in self.properties.items():
            objs[name] = DevicePropertyWidget(name, obj, parent=self, debug=self.DEBUG)
        # now add them all to stacked widget
        objs[None] = DevicePropertyWidget(None, {}, parent=self, debug=self.DEBUG)
        objs["NotExist"] = DevicePropertyWidget("NotExist", {}, parent=self, debug=self.DEBUG)
        self.widgets = objs
        for name, widget in objs.items():
            self.stacked.addWidget(widget)



    def change_device(self, text):
        id = self.deviceComboBox.findText(text)
        name = self.deviceComboBox.currentData()
        if name in self.widgets.keys():
            self.stacked.setCurrentWidget(self.widgets[name])
            self.currentDevice = name
            self.refresh_properties()
        else:
            self.stacked.setCurrentWidget(self.widgets["NotExist"])
            self.currentDevice = "NotExist"
        #turns out this is not needed, as on every command it gets current device


        # to remove item self.deviceComboBox.removeItem(id)
    # following was REMOVED, floored till next commit
    # def change_setting(self, *args):
    #     print(args)

    # def create_selector(self, name, items):
    #     ret = QtGui.QComboBox()
    #     ret.addItems(items)
    #     ret.setObjectName(name)
    #     ret.activated[str].connect(self.change_setting)
    #     return ret
    #
    # def create_float(self, name, range):
    #     ret = QtGui.QLineEdit()
    #     float_validator = Qt.QDoubleValidator(range[0], range[1], 6, ret)
    #     ret.setObjectName(name)
    #     ret.setValidator(float_validator)
    #     return ret
    #
    # def create_int(self, name, range):
    #     ret = QtGui.QLineEdit()
    #     ret.setObjectName(name)
    #     float_validator = Qt.QIntValidator(range[0], range[1])
    #     ret.setValidator(float_validator)
    #     return ret
    #
    # def create_label(self, text):
    #     ret = QtGui.QLabel(text)
    #     return ret


    def create_footer(self):
        layout = QtGui.QFormLayout()
        save = QtGui.QPushButton("Save")
        refresh = QtGui.QPushButton("Refresh")

        save.clicked.connect(self.save_properties)
        refresh.clicked.connect(self.refresh_properties)

        #layout.addWidget(save)
        #layout.addWidget(refresh)

        layout.addRow(save, refresh)

        return layout

    def save_properties(self, *args):
        current_device = self.deviceComboBox.currentIndex()
        if current_device == -1: #this means there are no connected devices
            return
        curr = self.widgets[self.currentDevice]
        obj = curr.get_properties()
        self.sanitized_list[current_device][2].set(obj)
        print("reminder to add save_properties stuff", obj)

    def refresh_properties(self, *args):
        try:
            current_device = self.deviceComboBox.currentIndex()
            if current_device == -1:
                return
            curr = self.widgets[self.currentDevice] # will be the same!
            data = self.sanitized_list[current_device][2].get()
            curr.set_properties(data)
        except:
            print(sys.exc_info())

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
            self.deviceComboBox.addItem(tuples[0]+" on "+tuples[1], tuples[0])
        # now time to set current choice if it is still in the list
        index = self.deviceComboBox.findText(text)
        if index != -1:
            self.deviceComboBox.setCurrentIndex(index)
        data = self.deviceComboBox.currentData()
        if data in self.widgets.keys():
            self.stacked.setCurrentWidget(self.widgets[data])
            self.currentDevice = data
            if index == -1:
                self.refresh_properties()
        else:
            self.stacked.setCurrentWidget(self.widgets["NotExist"])
            self.currentDevice = "NotExist"
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
    #return #we dont want this to happen yet
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = PropertiesWidget(parent)

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
    if not DEBUG:
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
    ex = PropertiesWidget()
    #ex = DevicePropertyWidget("AH", {}, debug=True)
    ex.show()
    #print(ex.get_properties())
    sys.exit(app.exec_())
