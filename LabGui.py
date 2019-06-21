# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 05:01:18 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file

nice logging example

http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python

"""
import sys
import os
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]))) # necessary for launching LabGui from another directory
from LabTools.IO import IOTool
from LabTools.Display import QtTools, PlotDisplayWindow, mplZoomWidget
from LabDrivers import Tool
from LabTools import DataManagement
from LabTools.DataStructure import LabeledData
from LocalVars import USE_PYQT5

# for commandwidget
from LabTools.CoreWidgets import CommandWidget

import getopt
from os.path import exists
import warnings
import time
import numpy as np
from collections import OrderedDict
import logging
import logging.config
from importlib import import_module

ABS_PATH = os.path.abspath(os.curdir)
#print(ABS_PATH)
try:
    logging.config.fileConfig(os.path.join(ABS_PATH, "logging.conf"))
except:
    logging.basicConfig()

if USE_PYQT5:

    from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                                 QFileDialog, QHBoxLayout, QApplication)

    import PyQt5.QtWidgets as QtGui

    from PyQt5.QtTest import QTest

    from PyQt5.QtGui import QIcon, QKeySequence
    # just grab the parts we need from QtCore
    from PyQt5.QtCore import Qt, QReadWriteLock, QSettings, pyqtSignal

else:

    from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QPushButton, QIcon,
                             QFileDialog, QHBoxLayout, QApplication)

    import PyQt4.QtGui as QtGui

    from PyQt4.QtTest import QTest

    from PyQt4.QtGui import QIcon, QKeySequence

    from PyQt4.QtCore import Qt, SIGNAL, QReadWriteLock, QSettings

PYTHON_VERSION = int(sys.version[0])
COREWIDGETS_PACKAGE_NAME = "LabTools"
USERWIDGETS_PACKAGE_NAME = "LabTools"
CONFIG_FILE = IOTool.CONFIG_FILE_PATH
DDT_CODE_STARTED = 'started'
DDT_CODE_RESUMED = 'resumed'
DDT_CODE_ALREADY_RUNNING = 'start_error'


class LabGuiMain(QtGui.QMainWindow):
    """

        This project was started in a lab with two sub teams having different experiments but using similar equipment,
        efforts were made to try capture what was the common core which should be shared and how to make sure we have
        the more modularity to be able to share the code with others.
        One thing is sure, we are physicists and not computer scientists, we learned python on the side and we might
        lack some standards in code writing/commenting, one of the reason we decided to share the code is to have you
        seeing the bugs and wierd features we don't notice anymore as we know how the code works internally.
        It would be greatly appreciated if you want to report those bugs or contribute.


        This is the main window in which all the widgets and plots are displayed and from which one manage the
        experiments

        It is a class and has certains attributes :
            -zoneCentrale which is a QMdiArea (where all your plot widget are going to be displayed)
            -instr_hub: a class (Tool.InstrumentHub) which is a collection of instruments
            -datataker : a class (DataManagment.DataTaker) which take data in a parallel thread so
            the plots do not freeze
            -cmdwin : a class widget which allow you to choose which instrument you want to place
            in your instrument hub
            -loadplotwidget : a class widget which allow loading of previously recorder data for visualization
            or fitting
            -startwidget : a class widger in which you select your script file and where to save, you can also
            start the experiment from this wigdet
            -dataAnalysewidget : a class widget used to do the fitting (this one is still in a beta mode and
            would need to be improved to be more flexible)
            -limitswidget : a class widget to visualise the values of the current plot axis limits in X and Y 
            -calc widget :
            -logTextEdit :

        All these instances are "connected" to the fp instance, so they exchange information
        with the use of QtCore.SIGNAL (read more about this in http://zetcode.com/gui/pyqt4/eventsandsignals/).

        You should have a file called config.txt with some keywords, the file config_example.txt contains them.

        This is a list of them with some explanation about their role. These don't need to be there, they will
        just make your life easier :)

            DEBUG= "if this is set to True, the instruments will not be actually connected to the computer,
            this is useful to debug the interface when away from your lab"
            SCRIPT="the path to the script and script name (.py) which contains the command you want
            to send and recieve to and from your instruments, basically this is where you set your experiment"
            SETTINGS="the path of the setting file and setting file name (.*) which contains your most used instrument
            connections so you don't have to reset them manually"
            DATAFILE="The path of the older data file and its name to load them into the plotting system"    
            SAMPLE= "this is simply the sample_name which will display automatically in the filename
            chosen to save the data
            DATA_PATH= "this is the path where the data should be saved"

            You can add any keyword you want and get what the value is using the function get_config_setting
            from the module IOTool

        The datataker instance will take care of executing the script you choosed when you click the
        "play"(green triangle) button or click "start" in the "Run Experiment"(startwidget) panel.
        The script is anything you want your instruments to do, a few examples are provided in the script
        folder under the names demo_*.py

        If measures are performed and you want to save them in a file and/or plot them, simply use the signal
        named "data(PyQt_PyObject)" in your script. The instance of LabGuiMain will catch it save it in a file
        and relay it through the signal "data_array_updated(PyQt_PyObject)"
        The data will always be saved if you use the signal "data(PyQt_PyObject)", and the filename will change
        automatically in case you stop the datataker and restart it, this way you will never erase your data.

        It is therefore quite easy to add your own widget which treats the data and do something else with them,
        you only need to connect it to the signal "data_array_updated(PyQt_PyObject)"
        and you will have access to the data.
        The comments about each widgets can be found in their respective modules.

        A wiki should be created to help understand and contribute to this project
    """
#    cmdwin = None
    if USE_PYQT5:
        # creating a signal
        debug_mode_changed = pyqtSignal(bool)

        triggered = pyqtSignal()

        colorsChanged = pyqtSignal('PyQt_PyObject')

        labelsChanged = pyqtSignal('PyQt_PyObject')
#        print(triggered.__dict__)

        markersChanged = pyqtSignal('PyQt_PyObject')

        selections_limits = pyqtSignal('PyQt_PyObject', int, int, int, int)

        data_array_updated = pyqtSignal('PyQt_PyObject')

        signal_remove_fit = pyqtSignal()

        DEBUG_mode_changed = pyqtSignal(bool)

        # should be loaded directly form InstrumentWidget

        instrument_hub_connected = pyqtSignal('PyQt_PyObject')

    def __init__(self, argv=[]):

        # run the initializer of the class inherited from6
        super(LabGuiMain, self).__init__()

        self.settings = QSettings(self)
        self.settings.setValue("state", self.saveState())

        # debug parameter used to run labgui even when there is no instrument
        # to connect to, used to plot past data or test the code
        self.DEBUG = True

        # variable to store the configfile name
        self.config_file = ''

        # variable to store the outputfile name
        self.output_file = ''

        # variable to store the display window handle
        self.current_pdw = None

        # variable containing the name of the instrument settings file
        self.instrument_connexion_setting_fname = ''

        # parse the argument(s) passed inline
        try:
            # option c is to provide a name for config file
            opts, args = getopt.getopt(argv, "c:")

            # loop through the arguments on the inline command
            for opt, arg in opts:

                # user passed configfile
                if opt == '-c':

                    self.config_file = arg

        except getopt.GetoptError:

            logging.error('configuration file : option -c argument missing')

        # verify if the config file passed by the user is valid and exists
        if self.config_file:

            if not exists(self.config_file):

                logging.error("The config file you provided ('%s') doesn't \
exist, '%s' will be used instead" % (self.config_file, CONFIG_FILE))

                warnings.warn("The config file you provided ('%s') doesn't \
exist, '%s' will be used instead" % (self.config_file, CONFIG_FILE))

                self.config_file = CONFIG_FILE

        else:

            # check whether the default config file exists or not
            if not exists(CONFIG_FILE):

                logging.warning("A '%s' file has been generated for you." % (
                    CONFIG_FILE))
                logging.warning("Please modify it to change the default \
    script, settings and data locations, or to enter debug mode.")

                # creates a config.txt with basic needs
                IOTool.create_config_file()

            # sets default config file name
            self.config_file = CONFIG_FILE

        # to make sure the config file is of the right format
        # ie that the user didn't specify the name of an existing file which
        # isn't a configuration file
        config_file_ok = False

        while not config_file_ok:

            try:
                # try to read the DEBUG parameter from the configuration file
                # as a test of the good formatting of the file
                self.DEBUG = IOTool.get_debug_setting(
                    config_file_path=self.config_file)

                # if this didn't generate errors we allow to get out of the loop
                config_file_ok = True

            except IOError:

                logging.error("The config file you provided ('%s') doesn't \
have the right format, '%s' will be used instead" % (self.config_file,
                                                     CONFIG_FILE))

                # check whether the default config file exists or not
                if not exists(CONFIG_FILE):
                    warnings.warn("A '%s' file has been generated for you." % (
                        CONFIG_FILE))
                    logging.warning("A '%s' file has been generated for you." % (
                        CONFIG_FILE))
                    logging.warning("Please modify it to change the default \
    script, settings and data locations, or to enter debug mode.")

                    # creates a config.txt with basic needs
                    IOTool.create_config_file()

                # sets default config file name
                self.config_file = CONFIG_FILE

        # load the parameter for the GPIB interface setting of the instruments
        interface = IOTool.get_interface_setting(
            config_file_path=self.config_file)

        # test if the parameter is correct
        if interface not in [Tool.INTF_VISA, Tool.INTF_PROLOGIX]:

            msg = """The %s variable of the config file '%s' is not correct
            The only two allowed values are : '%s' and '%s' """ % (
                IOTool.GPIB_INTF_ID,
                self.config_file,
                Tool.INTF_VISA,
                Tool.INTF_PROLOGIX
            )
            logging.warning(msg)
            # default setting
            Tool.INTF_GPIB = Tool.INTF_VISA # DEFAULT SHOULD BE PYVISA, MUCH MORE COMPATIBLE

        else:

            Tool.INTF_GPIB = interface

        if self.DEBUG:

            #            print("*" * 20)
            #            print("Debug mode is set to True")
            #            print("*" * 20)

            self.option_display_debug_state()

        else:

            self.option_display_normal_state()

        # create the central part of the application
        self.zoneCentrale = QtGui.QMdiArea()
        self.zoneCentrale.subWindowActivated.connect(
            self.update_current_window)
        self.setCentralWidget(self.zoneCentrale)

        # the lock is something for multithreading... not sure if it's important in our application.
        self.lock = QReadWriteLock()

        # InstrumentHub is responsible for storing and managing the user
        # choices about which instrument goes on which port
        self.instr_hub = Tool.InstrumentHub(parent=self,
                                            debug=self.DEBUG)

        # DataTaker is responsible for taking data from instruments in the
        # InstrumentHub object
        self.datataker = DataManagement.DataTaker(self.lock, self.instr_hub)

        self.cmdline = CommandWidget.CommandWidget(parent=self)
        self.cmddock = None
        #self.cmdline.instr_hub = self.instr_hub

        # handle data emitted by datataker (basically stuff it into a shared,
        # central array)
        if USE_PYQT5:

            self.datataker.data.connect(self.update_data_array)

            self.datataker.script_finished.connect(self.DTT_script_finished)

        else:

            self.connect(self.datataker, SIGNAL(
                "data(PyQt_PyObject)"), self.update_data_array)

            self.connect(self.datataker, SIGNAL(
                "script_finished(bool)"), self.DTT_script_finished)

        # the array in which the data will be stored
        self.data_array = np.array([])

        # all actions related to the figure widget (mplZoomWidget.py) are
        # set up in the actionmanager
        self.action_manager = mplZoomWidget.ActionManager(self)

        # this will contain the widget of the latest pdw created upon
        # connecting the instrument Hub
        self.actual_pdw = None

        # this will contain windows settings (labels, checkboxes states, colors)
        # of the plotdisplaw window which is created when the user click on
        # the connect button
        self.plot_window_settings = None

# set up menus and toolbars

        self.fileMenu = self.menuBar().addMenu("File")
        self.plotMenu = self.menuBar().addMenu("&Plot")
        self.instMenu = self.menuBar().addMenu("&Meas/Connect")
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.optionMenu = self.menuBar().addMenu("&Options")

        self.loggingSubMenu = self.optionMenu.addMenu("&Logger output level")
        self.intfSubMenu = self.optionMenu.addMenu("&GPIB interface")

        # Contains the zooming options buttons
        self.plotToolbar = self.addToolBar("Plot")

        # Contains the Start, Stop and Pause buttons
        self.instToolbar = self.addToolBar("Instruments")

        # start/stop/pause buttons
        self.start_DTT_action = QtTools.create_action(
            self, "Start DTT", slot=self.start_DTT,
            shortcut=QKeySequence("F5"), icon="start",
            tip="Start script")

        self.stop_DTT_action = QtTools.create_action(
            self, "Stop DTT", slot=self.stop_DTT,
            shortcut=QKeySequence("F6"), icon="stop",
            tip="stop script")

        self.pause_DTT_action = QtTools.create_action(
            self, "Pause DTT", slot=self.pause_DTT,
            shortcut=QKeySequence("F7"), icon="pause",
            tip="pause script")

        self.pause_DTT_action.setEnabled(False)
        self.stop_DTT_action.setEnabled(False)

        self.instToolbar.setObjectName("InstToolBar")

        self.instToolbar.addAction(self.start_DTT_action)
        self.instToolbar.addAction(self.pause_DTT_action)
        self.instToolbar.addAction(self.stop_DTT_action)

        # this will contain the different widgets in the window
        self.widgets = {}

        cur_path = os.path.dirname(__file__)

        # find the path to the widgets folders
        widget_path = os.path.join(cur_path, 'LabTools')

        # these are widgets essential to the interface
        core_widget_path = os.path.join(widget_path, 'CoreWidgets')

        # these are widgets which were added by users
        user_widget_path = os.path.join(widget_path, 'UserWidgets')


        # this is the legitimate list of core widgets
        widgets_list = [o.rstrip('.py') for o in os.listdir(core_widget_path)
                        if o.endswith(".py") and "__init__" not in o]

        # this is the legitimate list of user widgets
        user_widgets_list = [o.rstrip('.py') for o in os.listdir(user_widget_path)
                             if o.endswith(".py") and "__init__" not in o]

        # the user widgets the user would like to run, given in the config file
        user_widgets = IOTool.get_user_widgets(
            config_file_path=self.config_file)

        if user_widgets:

            for user_widget in user_widgets:
                # check that the given widget is legitimate
                if user_widget in user_widgets_list:
                    # add the given widget to the widget list which will be
                    # loaded
                    widgets_list.append(user_widget)

                else:

                    logging.warning("The user widget '%s' is not found at %s" % (
                        user_widget, user_widget_path))

        # add the widgets to the interface
        for widget in widgets_list:

            widget_name = widget

            try:
                widget_module = import_module(widget_name,
                                              package=COREWIDGETS_PACKAGE_NAME)
            except ImportError:

                widget_module = import_module(widget_name,
                                              package=USERWIDGETS_PACKAGE_NAME)

            try:

                self.add_widget(widget_module.add_widget_into_main)

            except AttributeError as e:

                logging.error(widget_module)
                raise e

# ##### FILE MENU SETUP ######

        self.file_save_settings_action = QtTools.create_action(
            self,
            "Save Instrument Settings",
            slot=self.file_save_settings,
            shortcut=QKeySequence.SaveAs,
            icon=None,
            tip="Save the current instrument settings"
        )

        self.file_load_settings_action = QtTools.create_action(
            self,
            "Load Instrument Settings",
            slot=self.file_load_settings,
            shortcut=QKeySequence.Open,
            icon=None,
            tip="Load instrument settings from file"
        )

        self.file_load_data_action = QtTools.create_action(
            self,
            "Load Previous Data",
            slot=self.file_load_data,
            shortcut=None,
            icon=None,
            tip="Load previous data from file"
        )

        self.file_save_config_action = QtTools.create_action(
            self,
            "Save current configuration",
            slot=self.file_save_config,
            shortcut=None,
            icon=None,
            tip="Save the setting file path, the script path and the data output path into the config file"
        )

        self.fileMenu.addAction(self.file_save_settings_action)
        self.fileMenu.addAction(self.file_load_settings_action)
        self.fileMenu.addAction(self.file_load_data_action)
        self.fileMenu.addAction(self.action_manager.saveFigAction)
        self.fileMenu.addAction(self.file_save_config_action)

# ##### PLOT MENU + TOOLBAR SETUP ######

        self.plotToolbar.setObjectName("PlotToolBar")

        for action in self.action_manager.actions:
            self.plotMenu.addAction(action)
            self.plotToolbar.addAction(action)

        self.clearPlotAction = QtTools.create_action(
            self,
            "Clear All Plots",
            slot=self.clear_plot,
            shortcut=None,
            icon="clear_plot",
            tip="Clears the live data arrays"
        )

        self.removeFitAction = QtTools.create_action(
            self,
            "Remove Fit",
            slot=self.remove_fit,
            shortcut=None,
            icon="clear",
            tip="Reset the fit data to an empty array"
        )

        self.plotMenu.addAction(self.clearPlotAction)
        self.plotMenu.addAction(self.removeFitAction)


# ##### INSTRUMENT MENU SETUP ######
        self.read_DTT = QtTools.create_action(
            self,
            "Read",
            slot=self.single_measure_DTT,
            shortcut=None,
            icon=None,
            tip="Take a one shot measure with DTT"
        )

        self.connect_hub = QtTools.create_action(
            self, "Connect Instruments",
            slot=self.connect_instrument_hub,
            shortcut=QKeySequence("Ctrl+I"),
            icon=None,
            tip="Refresh the list of selected instruments"
        )

        self.refresh_ports_list_action = QtTools.create_action(
            self,
            "Refresh ports list",
            slot=self.refresh_ports_list,
            icon=None,
            tip="Refresh the list of availiable ports"
        )

        self.instMenu.addAction(self.start_DTT_action)
        self.instMenu.addAction(self.read_DTT)
        self.instMenu.addAction(self.connect_hub)
        self.instMenu.addAction(self.refresh_ports_list_action)


# ##### WINDOW MENU SETUP ######
        self.add_pdw = QtTools.create_action(
            self,
            "Add a Plot",
            slot=self.create_pdw,
            shortcut=None,
            icon=None,
            tip="Add a recordsweep window"
        )

        self.windowMenu.addAction(self.add_pdw)

# ##### OPTION MENU SETUP ######
        self.toggle_debug_state = QtTools.create_action(
                self,
                "Change debug mode",
                slot=self.option_change_debug_state,
                shortcut=None,
                icon=None,
                tip="Change the state of the debug mode"
        )

        self.optionMenu.addAction(self.toggle_debug_state)

        self.toggle_cmd_state = QtTools.create_action(
            self,
            "Open GPIB CommandLine",
            slot=self.option_command_window_state,
            shortcut=None,
            icon=None,
            tip="Launch or focus GPIB CommandLine"
        )
        self.optionMenu.addAction(self.toggle_cmd_state)


        # Option to change the logging level displayed in the console
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            action = QtTools.create_action(
                self,
                log_level,
                slot=self.option_change_log_level,
                shortcut=None,
                icon=None,
                tip="Change the state of the logger to %s" % log_level
            )
            self.loggingSubMenu.addAction(action)

        # Option to change the interface of connexion for GPIB
        for interface in [Tool.INTF_VISA, Tool.INTF_PROLOGIX]:
            action = QtTools.create_action(
                self,
                interface,
                slot=self.option_change_interface,
                shortcut=None,
                icon=None,
                tip="Change the GPIB interface to %s" % interface
            )
            self.intfSubMenu.addAction(action)
###############################

        # Load the user settings for the instrument connectic and parameters
        self.default_settings_fname = IOTool.get_settings_name(
            config_file_path=self.config_file)

        if not exists(self.default_settings_fname):

            logging.warning("The filename '%s' wasn't found, using '%s'" % (
                self.default_settings_fname, 'settings/default_settings.txt'))

            self.default_settings_fname = 'settings/default_settings.txt'

        if os.path.isfile(self.default_settings_fname):

            logging.debug("Using '%s' as setting file" % (
                self.default_settings_fname))

            self.widgets['CalcWidget'].load_settings(
                self.default_settings_fname)

            self.widgets['InstrumentWidget'].load_settings(
                self.default_settings_fname)

        else:

            logging.warning("The chosen file '%s' is not a setting file" % (
                self.default_settings_fname))

        # Create the object responsible to display information send by the
        # datataker
        self.data_displayer = DataManagement.DataDisplayer(self.datataker)

        # platform-independent way to restore settings such as toolbar positions,
        # dock widget configuration and window size from previous session.
        # this doesn't seem to be working at all on my computer (win7 system)
        self.settings = QSettings("Gervais Lab", "LabGui")
        try:
            self.restoreState(self.settings.value("windowState").toByteArray())
            self.restoreGeometry(self.settings.value("geometry").toByteArray())
        except:
            logging.debug('Using default window configuration')
            # no biggie - probably means settings haven't been saved on this machine yet
            # hide some of the advanced widgets so they don't show for new users
            # the objects are not actually deleted, just hidden

    def add_widget(self, widget_creation, action_functions=None, **kwargs):
        """adds a widget to the MainArea Window

        this is a rough stage of this function, it calls a function from
        another module to add its widget to the Qdocks

        """
        widget_creation(self)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure you want to quit?", QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:

            # save the current settings
            self.file_save_settings(self.default_settings_fname)

            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.remove("script_name")
            event.accept()

        else:
            event.ignore()

    def create_pdw(self, num_channels=None, settings=None):
        """
            add a new plot display window in the MDI area its channels are labeled according to the channel names
            on the cmd window.
            It is connected to the signal of data update.
        """

        if num_channels is None:

            num_channels = self.instr_hub.get_instrument_nb() + \
                self.widgets['CalcWidget'].get_calculation_nb()

        pdw = PlotDisplayWindow.PlotDisplayWindow(data_array=self.data_array,
                                                  name="Live Data Window",
                                                  default_channels=num_channels)

        if USE_PYQT5:

            self.data_array_updated.connect(pdw.update_plot)

            pdw.mplwidget.limits_changed.connect(self.emit_axis_lim)

            # this is here temporary, I would like to change the plw when the live
            # fit is ticked

            self.widgets['AnalyseDataWidget'].update_fit.connect(
                pdw.update_fit)

            self.signal_remove_fit.connect(pdw.remove_fit)

            self.colorsChanged.connect(pdw.update_colors)

            self.labelsChanged.connect(pdw.update_labels)

            self.markersChanged.connect(pdw.update_markers)

        else:

            self.connect(self, SIGNAL("data_array_updated(PyQt_PyObject)"),
                         pdw.update_plot)

            self.connect(pdw.mplwidget, SIGNAL(
                "limits_changed(int,PyQt_PyObject)"), self.emit_axis_lim)

            # this is here temporary, I would like to change the plw when the live
            # fit is ticked

            self.connect(self.widgets['AnalyseDataWidget'], SIGNAL(
                "update_fit(PyQt_PyObject)"), pdw.update_fit)

            self.connect(self, SIGNAL("remove_fit()"), pdw.remove_fit)

            self.connect(self, SIGNAL("colorsChanged(PyQt_PyObject)"),
                         pdw.update_colors)

            self.connect(self, SIGNAL("labelsChanged(PyQt_PyObject)"),
                         pdw.update_labels)

            self.connect(self, SIGNAL(
                "markersChanged(PyQt_PyObject)"), pdw.update_markers)

        if settings is None:

            self.update_labels()
            self.update_colors()

        else:
            # this will set saved settings for the channel controls of the
            # plot display window
            pdw.set_channels_values(settings)

        self.zoneCentrale.addSubWindow(pdw)

        pdw.show()

    def get_last_window(self, window_ID="Live"):
        """
        should return the window that was created when the 
        instrument hub was connected
        """

        try:

            pdw = self.zoneCentrale.subWindowList()[-1].widget()

            return pdw

        except IndexError:

            logging.error("No pdw available")

    def update_colors(self):
        color_list = self.widgets['InstrumentWidget'].get_color_list() \
            + self.widgets['CalcWidget'].get_color_list()

        if USE_PYQT5:

            self.colorsChanged.emit(color_list)

        else:

            self.emit(SIGNAL("colorsChanged(PyQt_PyObject)"), color_list)

    def update_labels(self):
        label_list = self.widgets['InstrumentWidget'].get_label_list() \
            + self.widgets['CalcWidget'].get_label_list()

        if USE_PYQT5:

            self.labelsChanged.emit(label_list)

        else:

            self.emit(SIGNAL("labelsChanged(PyQt_PyObject)"), label_list)

    def emit_axis_lim(self, mode, limits):
        """
            emits the limits of the selected axis on the highlighted plot
        """
        current_window = self.zoneCentrale.activeSubWindow()

        if current_window:
            current_widget = self.zoneCentrale.activeSubWindow().widget()

        # this is a small check that we are no trying to get the limits from
        # the wrong plot
#            if current_widget.windowTitle() == "Past Data Window":
            try:
                paramX = current_widget.get_X_axis_index()
            except:
                paramX = 0
            try:
                paramY = current_widget.get_Y_axis_index()
            except:
                paramY = 1
            try:
                paramYfit = current_widget.get_fit_axis_index()
            except:
                paramYfit = 1
#
            try:
                #                logging.warning("%i%i"%(paramX,paramY))
                x = current_widget.data_array[:, paramX]
                xmin = limits[0][0]
                xmax = limits[0][1]
                imin = IOTool.match_value2index(x, xmin)
                imax = IOTool.match_value2index(x, xmax)

                if USE_PYQT5:

                    self.selections_limits.emit(
                        np.array([imin, imax, xmin, xmax]),
                        paramX, paramY, paramYfit, mode)

                else:

                    self.emit(SIGNAL(
                        "selections_limits(PyQt_PyObject,int,int,int,int)"),
                        np.array([imin, imax, xmin, xmax]),
                        paramX, paramY, paramYfit, mode)

            except IndexError:
                logging.debug("There is apparently no data generated yet")
            except:
                logging.warning("There was an error with the limits")

    def single_measure_DTT(self):

        self.datataker.initialize()
        self.datataker.read_data()
        self.datataker.ask_to_stop()

    def start_DTT(self):

        if not self.datataker.isRunning():

            # forbid the user to connect instruments to the hub while measuring
            self.widgets['InstrumentWidget'].bt_connecthub.setEnabled(False)

            # just update the color boxes in case
            self.update_colors()
            self.update_labels()

            # read the name of the output file and determine if it exists
            of_name = self.widgets['OutputFileWidget'].get_output_fname()
            is_new_file = not os.path.exists(of_name)

            # if this file is new, the first 2 lines contain the instrument and
            # parameters list
            if is_new_file:

                self.output_file = open(of_name, 'w')
                [instr_name_list, dev_list, param_list] = self.collect_instruments()
                self.output_file.write(
                    "#C"
                    + str(self.widgets['InstrumentWidget'].get_label_list()).strip('[]')
                    + '\n')
                self.output_file.write(
                    "#I"
                    + str(self.widgets['InstrumentWidget'].get_descriptor_list()).strip('[]')
                    + '\n')

                self.output_file.write(
                    "#P"
                    + str(param_list).strip('[]')
                    + '\n')

            else:
                # here I want to perform a check to see whether the number of instrument match
                # open it in append mode, so it won't erase previous data
                self.output_file = open(of_name, 'a')

            self.datataker.initialize(is_new_file)
            self.datataker.set_script(
                self.widgets['ScriptWidget'].get_script_fname()
            )

            # this command is specific to Qthread, it will execute whatever is defined in
            # the method run() from DataManagement.py module
            self.datataker.start()

            # Enable/disable the start, pause, stop buttons on the MainWindow
            self.start_DTT_action.setEnabled(False)
            self.pause_DTT_action.setEnabled(True)
            self.stop_DTT_action.setEnabled(True)

            return DDT_CODE_STARTED

        elif self.datataker.isPaused():
            # restarting from pause

            self.datataker.resume()

            self.start_DTT_action.setEnabled(False)
            self.pause_DTT_action.setEnabled(True)
            self.stop_DTT_action.setEnabled(True)

            return DDT_CODE_RESUMED

        else:

            print("Couldn't start datataker - already running!")
            print("Running: %s" % (self.datataker.isRunning()))
            print("Paused: %s" % (self.datataker.isPaused()))
            print("Stopped: %s" % (self.datataker.isStopped()))
            return DDT_CODE_ALREADY_RUNNING

    def pause_DTT(self):
        #        if not self.datataker.isStopped():
        #
        self.datataker.pause()

        self.start_DTT_action.setEnabled(True)
        self.pause_DTT_action.setEnabled(False)
        self.stop_DTT_action.setEnabled(True)

    def stop_DTT(self):

        if self.datataker.isRunning():

            self.datataker.ask_to_stop()

        # just make sure the pause setting is left as false after ther run
        self.start_DTT_action.setEnabled(True)
        self.pause_DTT_action.setEnabled(False)
        self.stop_DTT_action.setEnabled(False)

        # Enable changes to the instrument connections
        self.widgets['InstrumentWidget'].bt_connecthub.setEnabled(True)

        # close the output file
        self.output_file.close()

        # reopen the output file to read its content
        self.output_file = open(self.output_file.name, 'r')
        data = self.output_file.read()
        self.output_file.close()

        # insert the comments written by the user in the first line
        self.output_file = open(self.output_file.name, 'w')
        self.output_file.write(
            self.widgets['OutputFileWidget'].get_header_text())
        self.output_file.write(data)
        self.output_file.close()

        self.widgets['OutputFileWidget'].increment_filename()

    def DTT_script_finished(self, completed):
        """signal triggered by the completion of the script

            if the script is not an infinite loop, when it ends it sends
            a signal which triggers this method

        """

        self.stop_DTT()

    def DTT_isRunning(self):
        """indicates whether the datataker is running or not"""
        return self.datataker.isRunning()

    def toggle_DTT(self):
        if self.datataker.isStopped():
            self.start_DTT()
        else:
            self.stop_DTT()

    def write_data(self, data_set):

        if self.output_file:
            if not self.output_file.closed:
                # a quick way to make a comma separated list of the values
                stri = str(data_set).strip('[]\n\r')
                # numpy arrays include newlines in their strings, get rid of
                # them.
                stri = stri.replace('\n', '')

                # np.loadtxt uses whitespace delimiter by default, so we do too
                stri = stri.replace(',', ' ')

                self.output_file.write(stri + '\n')
                print('>>' + stri)

    def update_data_array(self, data_set):
        """ slot for when the thread emits data """

        # convert this latest data to an array
        data = np.array(data_set)

        for calculation in self.widgets['CalcWidget'].get_calculation_list():
            calculation = calculation.strip()
            if calculation:
                data = np.append(data, eval(calculation + '\n'))

        # writes data and calculated columns
        self.write_data(data.tolist())

        # check if this is the first piece of data
        if self.data_array.size == 0:
            self.data_array = data

            # need to make sure the shape is 2D even though there's only
            # one line of data so far
            self.data_array.shape = [1, self.data_array.size]
        else:
            # vstack just appends the data
            try:
                self.data_array = np.vstack([self.data_array, data])
            except:
                self.data_array = data

        if USE_PYQT5:

            self.data_array_updated.emit(self.data_array)

        else:

            self.emit(SIGNAL("data_array_updated(PyQt_PyObject)"),
                      self.data_array)

#

    def collect_instruments(self):
        """list properties of the connected instruments (comport, parameter)"""
        return self.widgets['InstrumentWidget'].collect_device_info()

    def refresh_ports_list(self):
        """Update the availiable port list in the InstrumentWindow module """

        self.widgets['InstrumentWidget'].refresh_cbb_port()

    def update_current_window(self):
        """
        this changes what self.<object> refers to so that the same shared toolbars can modify
        whichever plot window has focus right now
        """

        current_window = self.zoneCentrale.activeSubWindow()

        if current_window:
            self.action_manager.update_current_widget(
                current_window.widget().mplwidget)

        if current_window is not None:
            current_widget = self.zoneCentrale.activeSubWindow().widget()

            window_type = getattr(current_widget, "window_type", "unknown")

            if window_type == "unknown":
                msg = "The type of PlotDisplayWindow '%s' is unknown" % (
                    window_type)
                raise ValueError(msg)
            else:

                if window_type in PlotDisplayWindow.PLOT_WINDOW_TYPE_PAST:

                    # get the title of the window
                    title = str(current_window.windowTitle())

                    # extract the file name from the window title
                    # see LoadPlotWidget for more info on that
                    load_fname = title.split(
                        PlotDisplayWindow.PLOT_WINDOW_TITLE_PAST)

                    load_fname = load_fname[1]

                    # replace the header text by the one stored in memory
                    self.widgets["loadPlotWidget"].header_text(
                        self.loaded_data_header[load_fname])

                    # update the file information in the widget
                    self.widgets["loadPlotWidget"].load_file_name(load_fname)

                # this is only used by Print Figure (which doesn't work anyways)
                self.current_pdw = current_widget

        else:
            # 20130722 it runs this part of the code everytime I click
            # somewhere else that inside the main window
            pass

    def clear_plot(self):
        self.data_array = np.array([])

        if USE_PYQT5:

            self.data_array_updated.emit(self.data_array)

        else:

            self.emit(SIGNAL("data_array_updated(PyQt_PyObject)"),
                      self.data_array)

    def remove_fit(self):

        if USE_PYQT5:

            self.signal_remove_fit.emit()

        else:

            self.emit(SIGNAL("remove_fit()"))

    def file_save_config(self):
        """
        this function get the actual values of parameters and save them into the config file
        """
        script_fname = str(
            self.widgets['ScriptWidget'].scriptFileLineEdit.text())
        IOTool.set_config_setting(
            IOTool.SCRIPT_ID, script_fname, self.config_file)

        output_path = os.path.dirname(
            self.widgets['OutputFileWidget'].get_output_fname())+os.path.sep
        IOTool.set_config_setting(
            IOTool.SAVE_DATA_PATH_ID, output_path, self.config_file)

        if not self.instrument_connexion_setting_fname == "":
            IOTool.set_config_setting(
                IOTool.SETTINGS_ID, self.instrument_connexion_setting_fname, self.config_file)

    def file_save_settings(self, fname=None):
        """save the settings for the instruments and plot window into a file

            the settings are instrument names, connection ports, parameters
            for the instrument and which axis to select for plotting, colors,
            markers, linestyles and user defined parameters for the window
        """
        if (fname is None) or (not fname):

            if USE_PYQT5:

                fname, fmt = QtGui.QFileDialog.getSaveFileName(
                    self, 'Save settings file as', './')
                fname = str(fname)

            else:

                fname = str(QtGui.QFileDialog.getSaveFileName(
                    self, 'Save settings file as', './'))

        if fname:

            # the plotdisplay window which was created when the instrument
            # hub was connected
            pdw = self.actual_pdw

            if pdw is not None:
                # get the windows channel control values
                pdw_settings = pdw.list_channels_values()

            else:
                # this will do nothing
                pdw_settings = []

            self.widgets['InstrumentWidget'].save_settings(fname, pdw_settings)

            self.instrument_connexion_setting_fname = fname

    def file_load_settings(self, fname=None, **kwargs):
        """load the settings for the instruments and plot window

            the settings are instrument names, connection ports, parameters
            for the instrument and which axis to select for plotting, colors,
            markers, linestyles and user defined parameters for the window
        """

        if (fname is None) or (not fname):

            if USE_PYQT5:

                fname, fmt = QFileDialog.getOpenFileName(
                    self, 'Open settings file', './')

                fname = str(fname)

            else:

                fname = str(QtGui.QFileDialog.getOpenFileName(
                    self, 'Open settings file', './'))

        if fname:

            self.plot_window_settings = \
                self.widgets['InstrumentWidget'].load_settings(fname)

            if self.plot_window_settings:
                self.instrument_connexion_setting_fname = fname

    def file_load_data(self):
        default_path = IOTool.get_config_setting("DATAFILE",
                                                 config_file_path=self.config_file)

        if not default_path:

            default_path = './'

        if USE_PYQT5:

            fname, fmt = QtGui.QFileDialog.getOpenFileName(
                self, 'Open settings file', default_path)

            fname = str(fname)

        else:

            fname = str(QtGui.QFileDialog.getOpenFileName(
                self, 'Open settings file', default_path))

        if fname:

            self.create_plw(fname)

    def file_print(self):
        self.current_pdw.print_figure(file_name=self.output_file.name)

    def option_display_debug_state(self):
        """Visualy let the user know the programm is in DEBUG mode"""

        self.setWindowIcon(
            QIcon('images/icon_debug_py%s.png' % PYTHON_VERSION))
        self.setWindowTitle(
            "-" * 3
            + "DEBUG MODE" + "-" * 3
            + " (python%s)" % PYTHON_VERSION
            + " (GPIB_INTF: %s)" % Tool.INTF_GPIB
            + " (Configuration file :%s)" % self.config_file
        )
        self.setWindowOpacity(0.92)

    def option_display_normal_state(self):
        """Visualy let the user know the programm is in DEBUG mode"""
        self.setWindowIcon(
            QIcon('images/icon_normal_py%s.png' % PYTHON_VERSION))
        self.setWindowTitle("LabGui (python%s)" % PYTHON_VERSION
                            + " (GPIB_INTF: %s)" % Tool.INTF_GPIB
                            + " (Configuration file :%s)" % self.config_file
                            )
        self.setWindowOpacity(1)

    def option_change_debug_state(self):
        """Togggle the debug state"""

        if self.DEBUG:
            self.option_display_normal_state()
            self.DEBUG = False

        else:
            self.option_display_debug_state()
            self.DEBUG = True

        # if DEBUG is false, the port list needs to be fetched
        self.refresh_ports_list()

        IOTool.set_config_setting(IOTool.DEBUG_ID,
                                  self.DEBUG,
                                  config_file_path=self.config_file)

        if USE_PYQT5:

            self.debug_mode_changed.emit(self.DEBUG)

        else:

            self.emit(SIGNAL("DEBUG_mode_changed(bool)"), self.DEBUG)


    def option_command_window_state(self):
        """launches or focuses commandline """
        if self.cmddock:
            self.cmddock.setFloating(True)
            self.cmddock.toggleViewAction()
            self.cmddock.show()
        else:
            self.cmdline.show()
            self.cmdline.update_devices()
            self.cmdline.raise_()


    def option_change_interface(self):
        """changes GPIB interface"""
        intf = str(self.sender().text())
        # changes the GPIB interface in the instrument hub so the next time
        # one connects instrument it will be through this interface
        try:
            if not isinstance(self.output_file, str): # else, output_file.close() will be run
                self.stop_DTT() # must stop and DC everything first
        except:
            print(sys.exc_info(), self.output_file)

        self.instr_hub.change_interface(intf)

        self.setWindowTitle("LabGui (python%s)" % PYTHON_VERSION
                            + " (GPIB_INTF: %s)" % Tool.INTF_GPIB
                            + " (Configuration file :%s)" % self.config_file
                            )

        print("Please note: You cannot use both interfaces at the same time.")
        # change this setting into the configuration file as well
        IOTool.set_config_setting(IOTool.GPIB_INTF_ID, intf)

    def option_change_log_level(self):
        """change the file logging.conf's logging level"""

        log_level = str(self.sender().text())

        IOTool.set_config_setting("level", log_level,
                                  os.path.join(ABS_PATH, "logging.conf"))

        logging.config.fileConfig(os.path.join(ABS_PATH, "logging.conf"))


def launch_LabGui():
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()
    ex.show()
    sys.exit(app.exec_())


def test_automatic_fitting():
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()
    ex.connect_instrument_hub()

    pdw = ex.zoneCentrale.subWindowList()[0].widget()

    pdw.channel_objects["groupBox_X"][1].setChecked(True)
    pdw.channel_objects["groupBox_Y"][2].setChecked(True)
    pdw.channel_objects["groupBox_fit"][2].setChecked(True)

    ex.toggle_DTT()

    # choose the linear fonction to fit
    ex.widgets['AnalyseDataWidget'].fitCombo.setCurrentIndex(2)
    ex.widgets['AnalyseDataWidget'].on_live_fitButton_clicked()

    ex.show()
    sys.exit(app.exec_())


def test_save_fig():
    """connect the Hub and save the figure"""
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()

    ex.connect_instrument_hub()

#    ex.action_manager.saveFigAction.triggered()
    ex.show()
    sys.exit(app.exec_())


def test_save_settings(idx=0):
    """connect the Hub and save the settings"""
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()

    if idx == 0:
        ex.connect_instrument_hub()

    ex.file_save_settings("test_settings.set")

    ex.show()
    sys.exit(app.exec_())


def test_load_previous_data(data_path=os.path.join(ABS_PATH, 'scratch', 'example_output.dat')):
    """
    open a new plot window with previous data
    """
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()

    ex.create_plw(data_path)

    ex.show()
    sys.exit(app.exec_())


def test_user_variable_widget():
    """
    open a new plot window with previous data
    """
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()

    ex.file_load_settings("test_settings.set")

    ex.connect_instrument_hub()

#    ex.widgets["userVariableWidget"].on_updateVariableButton_clicked()

    ex.show()
    sys.exit(app.exec_())



def build_test():

    app = QtGui.QApplication(sys.argv)
    form = LabGuiMain()

    widget_start = form.instToolbar.widgetForAction(
        form.start_DTT_action)

    widget_stop = form.instToolbar.widgetForAction(
        form.stop_DTT_action)

    form.file_load_settings("test_settings.set")

    form.connect_instrument_hub()

    print("Intruments in the hub")
    print(form.instr_hub.get_instrument_nb())

    # Start the DTT
    QTest.mouseClick(widget_start, Qt.LeftButton)

    # print the name of the data file
    ofname = form.output_file.name
    print("DTT output file : %s" % ofname)
#    time.sleep(1)

#    QTest.mouseClick(widget_stop, Qt.LeftButton)
    """
    the script launches from cliking on start which triggers Datataker.run
    when the script is finished it emits script_finished(bool) with the value completed = True
    this is catched by the stop_DTT function from LabGui which then call stop_DTT from LabGui
    which then calls datataker.stop and datataker.resume
    this should probably be done be done within the Datataker class and only the reenabling of the 
    buttons should be done here...
    """
    form.show()
    sys.exit(app.exec_())


def test_stop_DTT_isrunning_false():

    app = QtGui.QApplication(sys.argv)
    form = LabGuiMain()


#    widget_start = form.instToolbar.widgetForAction(
#                                form.start_DTT_action)
#
#    widget_stop = form.instToolbar.widgetForAction(
#                                form.stop_DTT_action)
#
#    form.file_load_settings("test_settings.set")
#
#    form.connect_instrument_hub()
#
#
#    print("Intruments in the hub")
#    print(form.instr_hub.get_instrument_nb())
#
#    script_widget = form.widgets['ScriptWidget']
#
#    print("Script fname")
#    print(script_widget.scriptFileLineEdit.text())

#    fname = "tests\scripts\script_test_DTT.py"

#    script_widget.scriptFileLineEdit.setText('')

#    QTest.keyClicks(script_widget.scriptFileLineEdit, fname)

#    print form.datataker.script_file_name

    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    #    print("Launching LabGUI")
    launch_LabGui()
#    test_stop_DTT_isrunning_false()
#    build_test()
#    test_save_fig()
#    a = import_module('ConsoleWidget')
#    print(a)
#
#    a = import_module('ConsoleWidget', package = "LabTools")
#    print(a)
#
#    a = import_module('ConsoleWidget', package = "LabTools.CoreWidgets")
#    print(a)
#    test_automatic_fitting()


#    test_load_previous_data(fname)

#    test_save_settings(0)
#    test_user_variable_widget()
