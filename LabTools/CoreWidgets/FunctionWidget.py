# -*- coding: utf-8 -*-
"""
Created on Jun 7 2019

@author: zackorenberg

A widget designed to read/write properties to machine.
"""

"""
Created for GervaisLabs
"""

import sys

from types import MethodType
import logging
import time

import LabDrivers.utils

import LabTools.IO.IOTool as IOTools

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui
    import PyQt5.QtGui as Qt

else:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore

from LabTools.Display import QtTools

import numpy as np

from collections import Iterable

try:
    from LabTools.Display import PlotDisplayWindow
    PLOT = True
except:
    PlotDisplayWindow = None
    print("Unable to import PlotDisplay, plotting offline. Must be run from LabGui root")
    PLOT = False

import sys
import io

DEBUG = False

class FunctionFormWidget(QtGui.QWidget):

    def __init__(self, device, function, parameters, parent=None, debug=False):
        super(FunctionFormWidget, self).__init__(parent=parent)

        #print(device, function, parameters)
        self.device = device
        self.function = function
        self.parameters = parameters
        self.required = {}
        self.defaults = {}

        self.ok_style = "background-color: white; color: back"
        self.bad_style = "background-color: red; color: white"

        # make scrollable
        self.bold_font = Qt.QFont()
        self.bold_font.setBold(True)

        self.layout = QtGui.QFormLayout()
        self.widgets = {}
        if function == None:
            label = QtGui.QLabel(self)
            label.setText("No Function currently selected")
            self.layout = QtGui.QVBoxLayout(self)
            self.layout.addWidget(label)
            self.setLayout(self.layout)
            return
        # parse parameters
        for obj in parameters:
            #print(obj)
            text = obj['name']
            if 'unit' in obj.keys():
                if obj['unit'] is not None:
                    text = text+"("+obj['unit']+")"
            elif 'units' in obj.keys():
                if obj['units'] is not None:
                    text = text + "(" + obj['units'] + ")"
            label = self.create_label(text)
            # do required
            if 'required' in obj.keys():
                self.required[obj['name']] = obj['required']
                if self.required[obj['name']] == True:
                    label.setFont(self.bold_font)
            else:
                self.required[obj['name']] = False # default
            # do default values
            if 'default' in obj.keys():
                self.defaults[obj['name']] = obj['default']
            else:
                self.defaults[obj['name']] = None

            if obj['type'] == 'text':
                qtobject = self.create_text(obj['name'], obj['range'])
            elif obj['type'] == 'float':
                qtobject = self.create_float(obj['name'], obj['range'])
            elif obj['type'] == 'int':
                qtobject = self.create_int(obj['name'], obj['range'])
            elif obj['type'] == 'selector':
                qtobject = self.create_selector(obj['name'], obj['range'])
            elif obj['type'] == 'bool':
                qtobject = self.create_selector(obj['name'], obj['range'])
            else:
                qtobject = self.create_label("Error")
            qtobject.setStyleSheet(self.ok_style)
            self.widgets[obj['name']] = qtobject
            self.layout.addRow(label, qtobject)
        #self.setWidget(self.layout)
        self.setLayout(self.layout)

    ### FORM ITEMS ###

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
        if type(range) == str:  # placeholder text
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

    ## EVENTS ##
    def change_setting(self, *args):
        #print(args)
        #unused for the moment:
        i=1
    ### for getting input values ###
    def get_input(self):
        ret = {}
        flag = True
        for name in self.widgets.keys():
            data = self.extract_data(self.widgets[name])
            if self.required[name]:
                if data == '' or data == None:
                    self.widgets[name].setStyleSheet(self.bad_style)
                    self.widgets[name].style().polish(self.widgets[name])
                    flag = False
                else:
                    self.widgets[name].setStyleSheet(self.ok_style) # incase it has been corrected
                    self.widgets[name].style().unpolish(self.widgets[name])
            else:
                if data == '':
                    data = None # so user only needs to check if it contains value
            ret[name] = data
        if flag:
            return ret
        else:
            return None

    def clear_input(self):
        for name, object in self.widgets.items():
            self.clear_data(object)

    def default_input(self):
        for name, object in self.widgets.items():
            if self.defaults[name] is not None:
                self.write_data(self.defaults[name], object)

    ### individual input stuff ###
    def write_data(self, data, qtobject):  # individual set type stuff
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
            print("Unknown type for ", data, ": ", typ)
        return qtobject  # add any other types to the if statement

    def extract_data(self, qtobject):  # individual get type stuff
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
        # return qtobject # If any other options are required, add em to if statement

    def clear_data(self, qtobject):
        # make this check the type, and return a value based on that
        typ = type(qtobject)
        if typ == QtGui.QComboBox:
            qtobject.setCurrentIndex(0)
        elif typ == QtGui.QLineEdit:
            qtobject.clear()
        elif typ == QtGui.QCheckBox:
            qtobject.setChecked(False)
        else:
            print("invalid type to clear")
        qtobject.setStyleSheet(self.ok_style)
        # return qtobject # If any other options are required, add em to if statement


class DeviceFunctionWidget(QtGui.QWidget):

    def __init__(self, device, function_obj, parent=None, debug=False):
        super(DeviceFunctionWidget, self).__init__(parent=parent)

        self.DEBUG = debug

        self.device = device

        self.parent = parent
        if self.DEBUG:
            self.functions = {
                'Function 1': [
                    {
                        'name':'TextEdit',
                        'type':'text',
                        'range':'Placeholder text',
                        'units':None,
                        'required':True
                    }, #param for text
                    {
                        'name':'Integer',
                        'type':'int',
                        'range':[-100, 100],
                        'units':'Z',
                        'required':True
                    }, #param for int
                    {
                        'name': 'Float',
                        'type': 'float',
                        'range': [-100, 100],
                        'units': 'R',
                        'required': True,
                        'default': 0.05
                    },  # param for float
                    {
                        'name': 'DropdownMenu',
                        'type': 'selector',
                        'range':['A','B','C'],
                        'units':None,
                        'required':True
                    }, # param for dropdown
                    {
                        'name': 'Boolean',
                        'type':'bool',
                        'range':True,
                        'units':None,
                        'required':True # shouldnt matter
                    } # param for boolean
                ]
            } # debug each type
        else:
            self.functions = function_obj

        self.layout = QtGui.QGridLayout(self)
        #self.layout
        self.prop_items = {}
        self.list_view = None
        self.stacked = QtGui.QStackedWidget(self)
        self.widgets = {}
        self.scrollareas = {}

        self.current_function = None #'Voltage Pulse Sweep'



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
            # create listview with all functions
            self.list_view = self.create_listview()
            #self.list_view.setMaximumWidth(150)
            # create form of items to be sent to its own scrollable widget
            # for iobj in self.functions:
            #     item = iobj['name']
            #     # print(item, iobj)
            #     text = self.create_label(item)
            #     if iobj['type'] == 'selection':
            #         qtobject = self.create_selector(item, iobj['range'])
            #     elif iobj['type'] == 'float':
            #         qtobject = self.create_float(item, iobj['range'])
            #     elif iobj['type'] == 'int':
            #         qtobject = self.create_int(item, iobj['range'])
            #     elif iobj['type'] == 'bool':
            #         qtobject = self.create_bool(item, iobj['range'])
            #     elif iobj['type'] == 'text':
            #         qtobject = self.create_text(item, iobj['range'])
            #     else:
            #         qtobject = None
            #         print("uh oh")
            #     self.prop_items[item] = qtobject
            #     #if qtobject:
            #     #    self.layout.addRow(text, qtobject)
            # create form with Run, Plot, and Clear
            # add functions to stacked


            # add functions
            self.addFunctions()
            # set current
            self.stacked.setCurrentWidget(self.scrollareas[self.current_function])
            # create buttons and do events
            self.run_btn, self.plot_btn, self.clear_btn, self.defaults_btn = self.create_footer()
            self.run_btn.clicked.connect(self.run_event)
            self.plot_btn.clicked.connect(self.plot_event)
            self.clear_btn.clicked.connect(self.clear_event)
            self.defaults_btn.clicked.connect(self.defaults_event)
            # add stuff to the layout
            self.layout.addWidget(self.list_view, 0, 0, 5, 1)
            self.layout.addWidget(self.stacked, 0, 1, 4, 4)
            self.layout.addWidget(self.run_btn,4,1, 1, 1)
            self.layout.addWidget(self.plot_btn,4,2, 1, 1)
            self.layout.addWidget(self.clear_btn,4,3, 1, 1)
            self.layout.addWidget(self.defaults_btn,4,4,1,1)
            # make the row/col stretch (aesthetics)
            for i in range(0, 5):
                self.layout.setRowStretch(i, 1)
                for j in range(1,5):
                    self.layout.setColumnStretch(j, 1)
            self.layout.setColumnStretch(0,2)


        self.setLayout(self.layout)


    ### init helper functions ###
    def addFunctions(self):
        for name, obj in self.functions.items():
            self.widgets[name] = FunctionFormWidget(self.device, name, obj, parent=self, debug=self.DEBUG)
            self.scrollareas[name] = QtGui.QScrollArea(self)
            self.scrollareas[name].setWidget(self.widgets[name])
            self.scrollareas[name].setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.scrollareas[name].setEnabled(True)
            self.scrollareas[name].setWidgetResizable(True)
            self.stacked.addWidget(self.scrollareas[name])
        self.widgets[None] = FunctionFormWidget(self.device, None, obj, parent=self, debug=self.DEBUG)
        self.widgets['NotExist'] = FunctionFormWidget(self.device, 'NotExist', obj, parent=self, debug=self.DEBUG)
        for name in [None, 'NotExist']:
            self.scrollareas[name] = QtGui.QScrollArea(self)
            self.scrollareas[name].setWidget(self.widgets[name])
            self.scrollareas[name].setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.scrollareas[name].setEnabled(True)
            self.scrollareas[name].setWidgetResizable(True)
            self.stacked.addWidget(self.scrollareas[name])


    ### events ###
    def run_event(self, *args):
        #print(args)
        #model_id = self.list_view.currentIndex()
        #funct_data = self.list_view_model.itemData(model_id)
        #name = self.list_view_model.objectName()
        #print(funct_data, name)
        data = self.widgets[self.current_function].get_input()
        if data == None: # if there was an error from the input
            return

        if self.current_function in self.functions.keys():
            try:
                rdata = self.parent.run_function(self.current_function, data)
            except:
                print("Error executing function: ",sys.exc_info()[0])
                print(sys.exc_info())
                # add alert box maybe?
                return
            #print(data)
            # here is where we save the data:
            self.save_data(rdata,data)
            #filename = IOTools.get_funct_save_name(self.device, self.current_function)
            #if self.parent.save_data(filename, rdata, function=self.current_function, device=self.device, params=data):
            #    print("Data saved to: "+filename)
            return rdata
    def save_data(self, data, params):
        filename = IOTools.get_funct_save_name(self.device, self.current_function)
        if self.parent.save_data(filename, data, self.parent.start_time, function=self.current_function, device=self.device, params=params):
            print("Data saved to: " + filename)
    def clear_event(self, *args):
        self.widgets[self.current_function].clear_input()
        #print(args)
    def plot_event(self, *args):
        try:
            data = self.run_event(*args)
            # now to plot data
            if PLOT:
                self.parent.plot_function(self.current_function, data)
            else:
                print("Unable to plot")
        except:
            print(sys.exc_info())


    def defaults_event(self, *args):
        self.widgets[self.current_function].default_input()


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
                #print("working")


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

    ### more events ###
    def change_setting(self, *args):
        print(args)
    def change_function(self, current, previous):
        item = self.list_view_model.data(current)
        #print(item)
        self.current_function = item
        #self.stacked.setCurrentWidget(self.scrollareas[item])
        self.change_stacked(item)
        #print(item.data())

    def change_stacked(self, name):
        self.stacked.setCurrentWidget(self.scrollareas[name])

    def create_listview(self):
        self.list_view = QtGui.QListView(self)
        model = Qt.QStandardItemModel(self.list_view)
        for name in self.functions.keys():
            item = Qt.QStandardItem(name)
            item.setSelectable(True)
            item.setData(name)
            item.setEditable(False)
            model.appendRow(item)


        self.list_view_model = model # just incase
        #self.list_view_model.itemChanged.connect(self.change_function)
        #self.list_view_model.itemChanged()
        self.list_view.setModel(self.list_view_model)
        self.list_view.setWordWrap(True)
        self.list_view.selectionModel().currentChanged.connect(self.change_function)

        return self.list_view

    def create_footer(self):
        run = QtGui.QPushButton("Run")
        plot = QtGui.QPushButton("Plot")
        clear = QtGui.QPushButton("Clear")
        defaults = QtGui.QPushButton("Defaults")
        return [run, plot, clear, defaults]

    ### FORM ITEMS ###

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




class FunctionWidget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features ;)"""

    def __init__(self, parent=None, debug=False):
        super(FunctionWidget, self).__init__()

        #self.DEBUG = debug
        if DEBUG:
            self.DEBUG = True
        else:
            self.DEBUG = debug
        self.functions = LabDrivers.utils.list_driver_functions()
        self.plot = LabDrivers.utils.list_driver_plot_axes() # none if none
        self.device_layouts = {}
        self.layouts = {}
        self.ports = {}

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
        #self.verticalLayout.addStretch()
        self.verticalLayout.addWidget(self.stacked)
        #self.verticalLayout.addStretch()
        #self.footer = self.create_footer()
        #self.verticalLayout.addLayout(self.footer)

        self.setLayout(self.verticalLayout)

        #self.console_text("Please enter GPIB command")

        self.instrument_list = {}
        self.sanitized_list = list() # tuple, (name, port, object)



        self.plot_window = []

        self.start_time = 0



        if parent is not None:
            self.parentClass = parent
            self.instr_hub = parent.instr_hub
        else:
            self.parentClass = None
            self.instr_hub = None
        #elif self.parentClass is None:
        #    self.instr_hub = None

        self.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum))


    # create focus in override to refresh devices
    def enterEvent(self, event):
        #using this enterEvent until I find a more effective way
        if self.parent:
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
        for name, obj in self.functions.items():
            objs[name] = DeviceFunctionWidget(name, obj, parent=self, debug=self.DEBUG)
        # now add them all to stacked widget
        objs[None] = DeviceFunctionWidget(None, {}, parent=self, debug=self.DEBUG)
        objs["NotExist"] = DeviceFunctionWidget("NotExist", {}, parent=self, debug=self.DEBUG)
        self.widgets = objs
        for name, widget in objs.items():
            self.stacked.addWidget(widget)



    def change_device(self, text):
        id = self.deviceComboBox.findText(text)
        name = self.deviceComboBox.currentData()
        if name in self.widgets.keys():
            self.stacked.setCurrentWidget(self.widgets[name])
            self.currentDevice = name
            #self.refresh_properties()
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


    def create_footer(self): # will not be used
        layout = QtGui.QFormLayout()
        save = QtGui.QPushButton("Save")
        refresh = QtGui.QPushButton("Refresh")

        save.clicked.connect(self.save_properties)
        refresh.clicked.connect(self.refresh_properties)

        #layout.addWidget(save)
        #layout.addWidget(refresh)

        layout.addRow(save, refresh)

        return layout

    def run_function(self, name, arguments):
        id = self.deviceComboBox.currentIndex()
        device = self.sanitized_list[id]
        #print(device)
        driver = device[2]
        self.start_time = time.time()
        data = driver.run(name, arguments)
        #print(name+" Data:", data)
        return data
        ### This is for generated functions, not supported yet ###
        if hasattr(driver, name) and callable(getattr(driver, name)):
            return getattr(driver, name)(*arguments)

        else:
            print("Error in function: ", name, arguments, device)
            return False

    def plot_function(self, name, data):
        npdata = np.array(data)
        channels = np.size(npdata)
        device = self.deviceComboBox.currentData()
        window_name = device + ": "+name
        #print(channels, 1)
        if self.plot[device] is None:
            labels = []
        else:
            labels = self.plot[device]
        pltw = PlotDisplayWindow.PlotDisplayWindow(self, npdata, window_name, default_channels=channels, labels=labels)
        self.plot_window.append(pltw)
        pltw.show()



    def update_instrument_list(self):
        if self.parentClass is not None:
            self.instrument_list = self.parentClass.instr_hub.get_instrument_list()
            #print(self.instrument_list)

            #print(self.parentClass.instr_hub.get_port_param_pairs())
            #print(self.parentClass.instr_hub.get_instrument_nb())

            z = self.instrument_list.items()
            self.ports = {}
            self.instr_dict = {}
            ports = list()
            instruments = list()
            names = list()
            for x, y in z:
                if x is not None and "ComputerTime" not in x:
                    ports.append(x)
                    instruments.append(self.instrument_list[x])
                    names.append(self.instrument_list[x].ID_name)
                    self.ports[self.instrument_list[x].ID_name] = x
                    self.instr_dict[self.instrument_list[x].ID_name] = self.instrument_list[x]
                    #print(x,self.instrument_list[x].ID_name)
            self.sanitized_list = list(zip(names, ports, instruments))
            return
        elif self.DEBUG:
            self.sanitized_list = {}
            print("Debug mode")

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
            return "Unable to join object: "+sys.exc_info()[0]


    def save_data(self, fname, data, start_time, device="", function="", params={}):
        try:
            ndata = np.array(data)
            params = ", ".join(["{}={}".format(key, value) for key, value in params.items()])
            #print(params)

            t_dev = "TIME[]"
            if (start_time - ndata[0][0]) < 30000000:  # dif between start time n first data point < about a year
                t_dev = t_dev + ".TIME"
            else:
                t_dev = t_dev + ".dt"

            llabels = []
            devices = [t_dev]
            if device in self.plot.keys():
                llabels = self.plot[device]
            headers = []



            if function != "":
                if params != "":
                    function = function + " (" + params + ")"
                headers.append("# "+function)
            elif params != "": #incase only params are passed
                headers.append("# "+params)

            if device != "":
                if device in self.ports.keys():
                    d_str = device+"["+self.ports[device]+"]"
                    for i in range(1, np.size(ndata,1)):
                        devices.append(d_str)
                    # Assuming that the first column is always time (as per specs)


                else:
                    print(self.ports)
                    for i in range(1, np.size(ndata,1)):
                        devices.append(device)
                headers.append("#I'" + ("', '".join(devices)) + "'")
            headers.append("#T'%s'"%(str(start_time)))
            if llabels:
                headers.append( "#C'"+("', '".join(self.plot[device]))+"'")
            else:
                headers.append( "#C'"+("', '".join([str(i+1) for i in range(0, np.size(ndata,1))]))+"'" )
            np.savetxt(fname, ndata, header="\n".join(headers), comments='')
            return True
        except:
            print("Exception occured: "+sys.exc_info()[1])
            return False




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

    mywidget = FunctionWidget(parent)

    # create a QDockWidget
    propDockWidget = QtGui.QDockWidget("Driver Functions", parent)
    propDockWidget.setObjectName("functionDockWidget")
    propDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        | QtCore.Qt.BottomDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['FunctionWidget'] = mywidget

    propDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, propDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(propDockWidget.toggleViewAction())

    # redirect print statements to show a copy on "console"
    sys.stdout = QtTools.printerceptor(parent)

    propDockWidget.resize(500,250)
    #if not DEBUG:
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
    ex = FunctionWidget(parent=None, debug=True)
    #ex = DevicePropertyWidget("AH", {}, debug=True)
    ex.show()
    #print(ex.get_properties())
    sys.exit(app.exec_())
