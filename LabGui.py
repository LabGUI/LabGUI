# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 05:01:18 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file

nice logging example

http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python

"""
import sys
import PyQt4.QtGui as QtGui

# just grab the parts we need from QtCore
from PyQt4.QtCore import Qt, SIGNAL, QReadWriteLock, QSettings
#from file_treatment_general_functions import load_experiment
import py_compile
#import plot_menu_and_toolbar

import os
from os.path import exists

import numpy as np
from collections import OrderedDict

import logging
import logging.config

ABS_PATH=os.path.abspath(os.curdir)
logging.config.fileConfig(os.path.join(ABS_PATH,"logging.conf"))

from importlib import import_module


from LabTools.IO import IOTool
from LabTools.Display import QtTools, PlotDisplayWindow, mplZoomWidget
from LabDrivers import Tool
from LabTools import DataManagement
from LabTools.DataStructure import LabeledData
#FORMAT ='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d -%(message)s'
#logging.basicConfig(level=logging.DEBUG,format=FORMAT)

PYTHON_VERSION = int(sys.version[0])

LABWIDGETS_PACKAGE_NAME = "LabTools.CoreWidgets"

CONFIG_FILE = IOTool.CONFIG_FILE

class LabGuiMain(QtGui.QMainWindow):
    """

        This project was started in a lab with two sub teams having different experiments but using similar equipment, efforts were made to try capture what was the common core which should be shared and how to make sure we have the more modularity to be able to share the code with others.
        One thing is sure, we are physicists and not computer scientists, we learned pyhton on the side and we might lack some standards in code writing/commenting, one of the reason we decided to share the code is to have you seeing the bugs and wierd features we don't notice anymore as we know how the code works internally.
        It would be greatly apreciated if you want to report those bugs or contribute.


        This is the main window in which all the widgets and plots are displayed and from which one manage the experiments

        It is a class and has certains attributes :
            -zoneCentrale which is a QMdiArea (where all your plot widget are going to be displayed)
            -instr_hub: a class (Tool.InstrumentHub) which is a collection of instruments
            -datataker : a class (DataManagment.DataTaker) which take data in a parallel thread so the plots do not freeze
            -cmdwin : a class widget which allow you to choose which instrument you want to place in your instrument hub
            -loadplotwidget : a class widget which allow loading of previously recorder data for visualization or fitting
            -startwidget : a class widger in which you select your script file and where to save, you can also start the experiment from this wigdet
            -dataAnalysewidget : a class widget used to do the fitting (this one is still in a beta mode and would need to be improved to be more flexible)
            -limitswidget : a class widget to visualise the values of the current plot axis limits in X and Y 
            -calc widget :
            -logTextEdit :

        All these instances are "connected" to the fp instance, so they exchange information with the use of QtCore.SIGNAL (read more about this in http://zetcode.com/gui/pyqt4/eventsandsignals/).

        You should have a file called config.txt with some keywords, the file config_example.txt contains them.

        This is a list of them with some explanation about their role. These don't need to be there, they will just make your life easier :)

            DEBUG= "if this is set to True, the instruments will not be actually connected to the computer, this is useful to debug the interface when away from your lab"
            SCRIPT="the path to the script and script name (.py) which contains the command you want to send and recieve to and from your instruments, basically this is where you set your experiment"
            SETTINGS="the path of the setting file and setting file name (.*) which contains your most used instrument connections so you don't have to reset them manually"
            DATAFILE="The path of the older data file and its name to load them into the plotting system"    
            SAMPLE= "this is simply the sample_name which will display automatically in the filename choosen to save the data
            DATA_PATH= "this is the path where the data should be saved"

            You can add any keyword you want and get what the value is using the function get_config_setting from the module IOTool

        The datataker instance will take care of executing the script you choosed when you click the "play"(green triangle) button or click "start" in the "Run Experiment"(startwidget) panel.
        The script is anything you want your instruments to do, a few examples are provided in the script folder under the names demo_*.py

        If measures are performed and you want to save them in a file and/or plot them, simply use the signal named "data(PyQt_PyObject)" in your script. The instance of LabGuiMain will catch it save it in a file and relay it through the signal "data_array_updated(PyQt_PyObject)"
        The data will always be saved if you use the signal "data(PyQt_PyObject)", and the filename will change automatically in case you stop the datataker and restart it, this way you will never erase your data.

        It is therefore quite easy to add your own widget which treats the data and do something else with them, you only need to connect it to the signal "data_array_updated(PyQt_PyObject)" and you will have access to the data.
        The comments about each widgets can be found in their respective modules.

        A wiki should be created to help understand and contribute to this project
    """
#    cmdwin = None

    outputfile = None
    
    DEBUG = True

    def __init__(self):
        # run the initializer of the class inherited from6
        super(LabGuiMain, self).__init__()

        self.settings = QSettings(self)
        self.settings.setValue("state", self.saveState())
        
        #check whether a config file exists or not
        if exists(CONFIG_FILE) == False:
            logging.warning("A config.txt file has been generated for you.")           
            logging.warning("Please modify it to change the default \
script, settings and data locations, or to enter debug mode.")

            path = os.path.dirname(os.path.realpath(__file__)) + os.sep
            
            # creates a config.txt with basic needs
            IOTool.create_config_file(main_dir = path)
                
        #create the central part of the application
        self.zoneCentrale = QtGui.QMdiArea()
        self.zoneCentrale.subWindowActivated.connect(self.update_current_window)
        self.setCentralWidget(self.zoneCentrale)

        #read the DEBUG parameter from the configuration file (True/False)
        self.DEBUG = IOTool.get_debug_setting()
       
        if self.DEBUG == True:
            print("*" * 20)
            print("Debug mode is set to True")
            print("*" * 20)
            self.option_display_debug_state()
        else:
            self.option_display_normal_state()
            
        #load the parameter for the GPIB interface setting of the instruments
        interface = IOTool.get_interface_setting()
        
        #test if the parameter is correct
        if interface not in [Tool.INTF_VISA,Tool.INTF_PROLOGIX]:
            msg = """The %s variable of the config file '%s' is not correct
            The only two allowed values are : '%s' and '%s' """%(
                                                        IOTool.GPIB_INTF_ID,
                                                        IOTool.CONFIG_FILE,
                                                        Tool.INTF_VISA,
                                                        Tool.INTF_PROLOGIX
                                                        )
            logging.warning(msg)
            Tool.INTF_GPIB = Tool.INTF_PROLOGIX
                                       
        else:            
            Tool.INTF_GPIB = interface
            
        print("*" * 20)
        print("The GPIB setting for connecting instruments is %s"%(
                    Tool.INTF_GPIB))
        print("*" * 20)

        # the lock is something for multithreading... not sure if it's important in our application.
        self.lock = QReadWriteLock()

        # InstrumentHub is responsible for storing and managing the user
        # choices about which instrument goes on which port
        self.instr_hub = Tool.InstrumentHub(parent = self,
                                            debug = IOTool.get_debug_setting())
        
        # DataTaker is responsible for taking data from instruments in the
        # InstrumentHub object
        self.datataker = DataManagement.DataTaker(self.lock, self.instr_hub)

        # handle data emitted by datataker (basically stuff it into a shared,
        # central array)
        self.connect(self.datataker, SIGNAL(
            "data(PyQt_PyObject)"), self.update_data_array)

        #a signal to signify the data taking script is over
        self.connect(self.datataker, SIGNAL(
            "script_finished(bool)"), self.finished_DTT)
            
        #the array in which the data will be stored
        self.data_array = np.array([])
        
        # all actions related to the figure widget (mplZoomWidget.py) are 
        # set up in the actionmanager
        self.action_manager = mplZoomWidget.ActionManager(self)
        
        #this will contain the widget of the latest pdw created upon
        #connecting the instrument Hub
        self.actual_pdw = None
        
        #this will contain windows settings (labels, checkboxes states, colors)
        #of the plotdisplaw window which is created when the user click on
        #the connect button
        self.plot_window_settings = None
        
#### set up menus and toolbars      
        
        self.fileMenu = self.menuBar().addMenu("File")
        self.plotMenu = self.menuBar().addMenu("&Plot")
        self.instMenu = self.menuBar().addMenu("&Meas/Connect")
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.optionMenu = self.menuBar().addMenu("&Options")
        
        self.loggingSubMenu = self.optionMenu.addMenu("&Logger output level")        
        
        self.plotToolbar = self.addToolBar("Plot")
        self.instToolbar = self.addToolBar("Instruments")
        
        
        # start/stop/pause buttons 
        self.start_DTT_action = QtTools.create_action(
            self, "Start DTT", slot = self.start_DTT, 
            shortcut = QtGui.QKeySequence("F5"), icon = "start",
            tip = "Start script")
            
        self.stop_DTT_action = QtTools.create_action(
            self, "Stop DTT", slot = self.stop_DTT,
            shortcut = QtGui.QKeySequence("F6"), icon = "stop",
            tip = "stop script")
            
        self.pause_DTT_action = QtTools.create_action(
            self, "Pause DTT", slot = self.pause_DTT, 
            shortcut = QtGui.QKeySequence("F7"), icon = "pause", 
            tip = "pause script")
            
        self.pause_DTT_action.setEnabled(False)
        self.stop_DTT_action.setEnabled(False)


        self.instToolbar.setObjectName("InstToolBar")

        self.instToolbar.addAction(self.start_DTT_action)
        self.instToolbar.addAction(self.pause_DTT_action)
        self.instToolbar.addAction(self.stop_DTT_action)        
        
        
        #this will contain the different widgets in the window
        self.widgets = {}
        
        cur_path = os.path.dirname(__file__)
        #    widget_path = os.path.join(cur_path,'LabTools')
        #    widget_path = os.path.join(widget_path,'Widgets')

        #find the path to the widgets folders
        widget_path = os.path.join(cur_path,'LabTools')
        
        #these are widgets essential to the interface
        core_widget_path = os.path.join(widget_path,'CoreWidgets')
        
        #these are widgets which were added by users
        user_widget_path = os.path.join(widget_path,'UserWidgets')
        
        widgets_list = [o for o in os.listdir(core_widget_path) 
                        if o.endswith(".py") and not "__init__" in o]

        #add the widgets to the interface
        for widget in widgets_list:
            
            widget_name = widget.rstrip('.py')
            widget_module = import_module("." + widget_name, 
                                          package = LABWIDGETS_PACKAGE_NAME)
            
            self.add_widget(widget_module.add_widget_into_main)        
        
        
###### FILE MENU SETUP ######

        self.fileSaveSettingsAction = QtTools.create_action(self,
        "Save Instrument Settings", slot = self.file_save_settings, 
        shortcut = QtGui.QKeySequence.SaveAs,
        icon = None, tip = "Save the current instrument settings")

        self.fileLoadSettingsAction = QtTools.create_action(self, 
        "Load Instrument Settings", slot = self.file_load_settings,
        shortcut = QtGui.QKeySequence.Open,
        icon = None, tip = "Load instrument settings from file")

        self.fileLoadDataAction = QtTools.create_action(self, 
        "Load Previous Data", slot = self.file_load_data, shortcut = None,
        icon = None, tip = "Load previous data from file")
                                                                    
        """this is not working I will leave it commented right now"""
#        self.filePrintAction = QtTools.create_action(self, "&Print Report", slot=self.file_print, shortcut=QtGui.QKeySequence.Print,
#                                                     icon=None, tip="Print the figure along with relevant information")
                
        self.fileSaveCongfigAction = QtTools.create_action(self,
        "Save current configuration", slot = self.file_save_config,
        shortcut = None, icon = None, tip = "Save the setting file path, \
the script path and the data output path into the config file")
        
        self.fileMenu.addAction(self.fileLoadSettingsAction)
        self.fileMenu.addAction(self.fileSaveSettingsAction)
        self.fileMenu.addAction(self.fileLoadDataAction)
#        self.fileMenu.addAction(self.filePrintAction)
        self.fileMenu.addAction(self.action_manager.saveFigAction)
        self.fileMenu.addAction(self.fileSaveCongfigAction)

###### PLOT MENU + TOOLBAR SETUP ######

        
        self.plotToolbar.setObjectName("PlotToolBar")
        

        for action in self.action_manager.actions:
            self.plotMenu.addAction(action)
            self.plotToolbar.addAction(action)

        self.clearPlotAction = QtTools.create_action(self, 
        "Clear All Plots", slot = self.clear_plot, shortcut = None,
        icon = "clear_plot", tip = "Clears the live data arrays")
                                                     
        self.removeFitAction = QtTools.create_action(self, 
        "Remove Fit", slot = self.remove_fit, shortcut = None,
        icon = "clear", tip = "Reset the fit data to an empty array")

        self.plotMenu.addAction(self.clearPlotAction)
        self.plotMenu.addAction(self.removeFitAction)


###### INSTRUMENT MENU SETUP ######
        self.read_DTT = QtTools.create_action(self, "Read", 
        slot = self.single_measure_DTT, shortcut = None, icon = None, 
        tip = "Take a one shot measure with DTT")
        
        
        self.connect_hub = QtTools.create_action(self, "Connect Instruments", 
        slot = self.connect_instrument_hub, 
        shortcut = QtGui.QKeySequence("Ctrl+I"), icon=None,
        tip="Refresh the list of selected instruments")

        self.refresh_ports_list_action = QtTools.create_action(self, 
        "Refresh ports list", slot = self.refresh_ports_list, icon = None,
        tip = "Refresh the list of availiable ports")

        
 
        self.instMenu.addAction(self.start_DTT_action)
        self.instMenu.addAction(self.read_DTT)
        self.instMenu.addAction(self.connect_hub)
        self.instMenu.addAction(self.refresh_ports_list_action)


###### WINDOW MENU SETUP ######
        self.add_pdw = QtTools.create_action(self, "Add a Plot",
        slot = self.create_pdw, shortcut = None, icon = None,
        tip = "Add a recordsweep window")
        
        
        self.add_pqtw = QtTools.create_action(self, "Add a PyQtplot",
        slot = self.create_pqtw, shortcut = None, icon = None,
        tip = "Add a pyqt window")


        self.windowMenu.addAction(self.add_pdw)
        
        try:
            
            import PyQTWindow
            self.windowMenu.addAction(self.add_pqtw)
            
        except:
            logging.info("pyqtgraph is unable to load, \
the pyqt window option is disabled")
        
###### OPTION MENU SETUP ######
        self.toggle_debug_state = QtTools.create_action(self, 
        "Change debug mode", slot = self.option_change_debug_state, 
        shortcut = None, icon = None,
        tip = "Change the state of the debug mode")
        
#        self.toggle_debug_state = QtTools.create_action(self, 
#        "Change debug mode", slot = self.option_change_debug_state, 
#        shortcut = None, icon = None,
#        tip = "Change the state of the debug mode")

        self.optionMenu.addAction(self.toggle_debug_state)
        
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            action = QtTools.create_action(self, 
            log_level, slot = self.option_change_log_level, 
            shortcut = None, icon = None,
            tip = "Change the state of the logger to %s" % log_level)
            
            self.loggingSubMenu.addAction(action)
        
###############################

        #Load the user settings for the instrument connectic and parameters
        self.default_settings_fname = 'settings/default_settings.txt'
        
        if os.path.isfile(self.default_settings_fname):  
            
            self.widgets['CalcWidget'].load_settings(
                    self.default_settings_fname)            
            
            self.widgets['InstrumentWidget'].load_settings(
                    self.default_settings_fname)
            
           

        # Create the object responsible to display information send by the
        # datataker
        self.data_displayer = DataManagement.DataDisplayer(self.datataker)

        # platform-independent way to restore settings such as toolbar positions,
        # dock widget configuration and window size from previous session.
        # this doesn't seem to be working at all on my computer (win7 system)
        self.settings = QSettings("Gervais Lab", "RecordSweep")
        try:
            self.restoreState(self.settings.value("windowState").toByteArray())
            self.restoreGeometry(self.settings.value("geometry").toByteArray())
        except:
            logging.info('Using default window configuration') # no biggie - probably means settings haven't been saved on this machine yet
            #hide some of the advanced widgets so they don't show for new users
            # the objects are not actually deleted, just hidden


    def add_widget(self,widget_creation,action_fonctions = None,**kwargs):
        """adds a widget to the MainArea Window
        
        this is a rough stage of this fonction, it calls a fonction from
        another module to add this widget
        
        """
        widget_creation(self)
        

            
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
        "Are you sure you want to quit?", QtGui.QMessageBox.Yes, 
        QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            
            #save the current settings
            self.file_save_settings(self.default_settings_fname)
            
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.remove("script_name")
            event.accept()

        else:
            event.ignore()

    def create_pdw(self, num_channels = None, settings = None):
        """
            add a new plot display window in the MDI area its channels are labeled according to the channel names on the cmd window.
            It is connected to the signal of data update.
        """
        
        if num_channels == None:
            
            num_channels = self.instr_hub.get_instrument_nb() + \
                           self.widgets['CalcWidget'].get_calculation_nb()
       
        pdw = PlotDisplayWindow.PlotDisplayWindow(data_array = self.data_array,
                                        name="Live Data Window",
                                        default_channels = num_channels)  
        
        self.connect(self, SIGNAL("data_array_updated(PyQt_PyObject)"),
                     pdw.update_plot)
                     
        self.connect(pdw.mplwidget, SIGNAL(
            "limits_changed(int,PyQt_PyObject)"), self.emit_axis_lim)

        # this is here temporary, I would like to change the plw when the live
        # fit is ticked
        self.connect(self.widgets['AnalyseDataWidget'], SIGNAL(
            "data_set_updated(PyQt_PyObject)"), pdw.update_plot)
        self.connect(self.widgets['AnalyseDataWidget'], SIGNAL(
            "update_fit(PyQt_PyObject)"), pdw.update_fit)
        self.connect(self, SIGNAL("remove_fit()"), pdw.remove_fit)

        self.connect(self, SIGNAL("colorsChanged(PyQt_PyObject)"),
                     pdw.update_colors)
        self.connect(self, SIGNAL("labelsChanged(PyQt_PyObject)"),
                     pdw.update_labels)
        self.connect(self, SIGNAL(
            "markersChanged(PyQt_PyObject)"), pdw.update_markers)
        
        if settings == None:
            
            self.update_labels()
            self.update_colors()
            
        else:
            #this will set saved settings for the channel controls of the 
            #plot display window
            pdw.set_channels_values(settings)

        self.zoneCentrale.addSubWindow(pdw)

        pdw.show()

    def create_pqtw(self):
        """
            add a new pqt plot display window in the MDI area its channels are labeled according to the channel names on the cmd window.
            It is connected to the signal of data update.
        """
        pqtw = PyQtWindow.PyQtGraphWidget(n_curves=self.instr_hub.get_instrument_nb(
        ) + self.widgets['CalcWidget'].get_calculation_nb(), parent=self)  # self.datataker)
        self.connect(self, SIGNAL("spectrum_data_updated(PyQt_PyObject,int)"),
                     pqtw.update_plot)
#        self.connect(pdw.mplwidget,SIGNAL("limits_changed(int,PyQt_PyObject)"),self.emit_axis_lim)

        # this is here temporary, I would like to change the plw when the live fit is ticked
#        self.connect(self.dataAnalyseWidget, SIGNAL("data_set_updated(PyQt_PyObject)"),pdw.update_plot)
#        self.connect(self.dataAnalyseWidget, SIGNAL("update_fit(PyQt_PyObject)"), pdw.update_fit)
#        self.connect(self,SIGNAL("remove_fit()"), pdw.remove_fit)

#        self.connect(self, SIGNAL("colorsChanged(PyQt_PyObject)"), pdw.update_colors)
#        self.connect(self, SIGNAL("labelsChanged(PyQt_PyObject)"), pdw.update_labels)
#        self.connect(self, SIGNAL("markersChanged(PyQt_PyObject)"), pdw.update_markers)
#        self.update_labels()
#        self.update_colors()

        self.zoneCentrale.addSubWindow(pqtw)

        pqtw.show()


    def get_last_window(self, window_ID = "Live"):
        """
        should return the window that was created when the 
        instrument hub was connected
        """
        
        try:
            
            pdw = self.zoneCentrale.subWindowList()[-1].widget()
        
        except IndexError:
            
            logging.error("No pdw available")
        
        return pdw
            

    def update_colors(self):
        color_list = self.widgets['InstrumentWidget'].get_color_list() \
                     + self.widgets['CalcWidget'].get_color_list()

        self.emit(SIGNAL("colorsChanged(PyQt_PyObject)"), color_list)

    def update_labels(self):
        label_list = self.widgets['InstrumentWidget'].get_label_list() \
                     + self.widgets['CalcWidget'].get_label_list()
                     
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
#                except:
#                    logging.info( "G2GUI.emit_axis_lim : the params are not defined, the default is X-> Channel 1 and Y->Channel 2")
                    
#            else:
#                try:
#                    paramX = current_widget.get_X_axis_index()
#                    paramY = current_widget.get_Y_axis_index()
#                    paramYfit = current_widget.get_fit_axis_index()
#                except:
#                    logging.info("G2GUI.emit_axis_lim : the params are not defined, the default is X-> Channel 1 and Y->Channel 2")
#                    paramX = 0
#                    paramY = 1
#                    paramYfit = 1
#            
            try:
#                logging.warning("%i%i"%(paramX,paramY))
                x = current_widget.data_array[:, paramX]
                xmin = limits[0][0]
                xmax = limits[0][1]
                imin = IOTool.match_value2index(x, xmin)
                imax = IOTool.match_value2index(x, xmax)
                self.emit(SIGNAL("selections_limits(PyQt_PyObject,int,int,int,int)"), np.array(
                    [imin, imax, xmin, xmax]), paramX, paramY, paramYfit, mode)
            except IndexError:
                logging.debug("There is apparently no data generated yet")
            except:
                logging.warning("There was an error with the limits")

    def single_measure_DTT(self):
        self.datataker.initialize()
        self.datataker.read_data()
        self.datataker.stop()

    def start_DTT(self):
        if self.datataker.isStopped():
            self.start_DTT_action.setEnabled(False)
            self.pause_DTT_action.setEnabled(True)
            self.stop_DTT_action.setEnabled(True)
            
            self.widgets['InstrumentWidget'].bt_connecthub.setEnabled(False)

            #self.startWidget.startStopButton.setText("Stop!")
            #self.start_DTT_.setText("Stop DTT")

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
                    "#C" + str(self.widgets['InstrumentWidget'].get_label_list()).strip('[]') + '\n')
                self.output_file.write(
                    "#I" + str(self.widgets['InstrumentWidget'].get_descriptor_list()).strip('[]') + '\n')

                self.output_file.write(
                    "#P" + str(param_list).strip('[]') + '\n')

            else:
                # here I want to perform a check to see whether the number of instrument match
                # open it in append mode, so it won't erase previous data
                self.output_file = open(of_name, 'a')
                
            self.datataker.initialize(is_new_file)
            self.datataker.set_script(self.widgets['SciptWidget'].get_script_fname())
            
            # this command is specific to Qthread, it will execute whatever is defined in
            # the method run() from DataManagement.py module
            self.datataker.start()

        elif self.datataker.isPaused():
            # restarting from pause
            self.start_DTT_action.setEnabled(False)
            self.pause_DTT_action.setEnabled(True)
            self.stop_DTT_action.setEnabled(True)

            self.datataker.resume()
        else:
            print("Couldn't start DTT - already running!")

    def stop_DTT(self):
        if not self.datataker.isStopped():
            self.datataker.resume()
            self.datataker.stop()
            
            #close the output file
            self.output_file.close()
            
            #reopen the output file to read its content
            self.output_file = open(self.output_file.name, 'r')
            data = self.output_file.read()
            self.output_file.close()
            
            #insert the comments written by the user in the first line
            self.output_file = open(self.output_file.name, 'w')
            self.output_file.write(self.widgets['OutputFileWidget'].get_header_text())
            self.output_file.write(data)
            self.output_file.close()
                       
            # just make sure the pause setting is left as false after ther run        
            self.start_DTT_action.setEnabled(True)
            self.pause_DTT_action.setEnabled(False)
            self.stop_DTT_action.setEnabled(False)

            # Enable changes to the instrument connections    
            self.widgets['InstrumentWidget'].bt_connecthub.setEnabled(True)
        else:
            print("Couldn't stop DTT - it wasn't running!")

    def pause_DTT(self):
        if not self.datataker.isStopped():
            self.start_DTT_action.setEnabled(True)
            self.pause_DTT_action.setEnabled(False)
            self.stop_DTT_action.setEnabled(True)
            self.datataker.pause()

    def toggle_DTT(self):
        if self.datataker.isStopped():
            self.start_DTT()
        else:
            self.stop_DTT()


    def finished_DTT(self, completed):
        if completed:
            self.start_DTT_action.setEnabled(True)
            self.pause_DTT_action.setEnabled(False)
            self.stop_DTT_action.setEnabled(False)

            self.widgets['OutputFileWidget'].increment_filename()
            
            # just make sure the pause setting is left as false after ther run
            self.datataker.resume()
            self.output_file.close()

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

    def update_spectrum_data(self, spectrum_data):
        chan_num = 0
        self.emit(SIGNAL("spectrum_data_updated(PyQt_PyObject)"),
                  spectrum_data, chan_num)

    def update_data_array(self, data_set):
        """ slot for when the thread emits data """

        # convert this latest data to an array
        data = np.array(data_set)

        for calculation in self.widgets['CalcWidget'].get_calculation_list():
            calculation = calculation.strip()
            if calculation:
                data = np.append(data, eval(calculation + '\n'))
            #else:
                #print "here's the zero"
                #data = np.append(data, 0)

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

        self.emit(SIGNAL("data_array_updated(PyQt_PyObject)"), self.data_array)

#   

    def collect_instruments(self):
        return self.widgets['InstrumentWidget'].collect_device_info()

    def refresh_ports_list(self):
        """Update the availiable port list in the InstrumentWindow module """

        self.widgets['InstrumentWidget'].refresh_cbb_port()


    def update_current_window(self, x):
        ''' this changes what self.<object> refers to so that the same shared toolbars can modify whichever plot window has focus right now '''        
        
        current_window = self.zoneCentrale.activeSubWindow()
        if current_window:
            self.action_manager.update_current_widget(
                        current_window.widget().mplwidget)
            
        if not current_window is None:
            current_widget = self.zoneCentrale.activeSubWindow().widget()
            
            window_type = getattr(current_widget, "window_type", "unknown")
            
            if window_type == "unknown":                
                msg = "The type of PlotDisplayWindow '%s' is unknown"%(window_type)
                raise ValueError(msg)
            else:     
                # this is only used by Print Figure (which doesn't work anyways)
                self.current_pdw = current_widget
                
                # this was only used by saveFig, at least within this file.
                self.fig = current_widget.fig
        else:
            # 20130722 it runs this part of the code everytime I click
            # somewhere else that inside the main window
            pass

    def isrunning(self):
        """indicates whether the datataker is running or not"""
        return not self.datataker.stopped

    def clear_plot(self):
        self.data_array = np.array([])
        self.emit(SIGNAL("data_array_updated(PyQt_PyObject)"), self.data_array)

    def remove_fit(self):
        self.emit(SIGNAL("remove_fit()"))

    def file_save_config(self):
        """
        this function get the actual values of parameters and save them into the config file
        """
        script_fname=str(self.widgets['SciptWidget'].scriptFileLineEdit.text())
        IOTool.set_config_setting(IOTool.SCRIPT_ID,script_fname,CONFIG_FILE)
        
        output_path = os.path.dirname(self.widgets['OutputFileWidget'].get_output_fname())+os.path.sep
        IOTool.set_config_setting(IOTool.SAVE_DATA_PATH_ID,output_path,CONFIG_FILE)
        
        if not self.instrument_connexion_setting_fname == "":
            IOTool.set_config_setting(IOTool.SETTINGS_ID,self.instrument_connexion_setting_fname,CONFIG_FILE)

    def file_save_settings(self, fname = None):
        """save the settings for the instruments and plot window into a file
        
            the settings are instrument names, connection ports, parameters
            for the instrument and which axis to select for plotting, colors,
            markers, linestyles and user defined parameters for the window
        """
        
        if fname == None:
            
            fname = str(QtGui.QFileDialog.getSaveFileName(
                self, 'Save settings file as', './'))
                
        if fname:
            
            #the plotdisplay window which was created when the instrument
            #hub was connected
            pdw = self.actual_pdw
            
            if not pdw == None:
                #get the windows channel control values
                pdw_settings = pdw.list_channels_values()
                
            else:
                #this will do nothing
                pdw_settings = []
                
            self.widgets['InstrumentWidget'].save_settings(fname, pdw_settings)
            
            self.instrument_connexion_setting_fname = fname

    def file_load_settings(self, fname = None):
        """load the settings for the instruments and plot window
        
            the settings are instrument names, connection ports, parameters
            for the instrument and which axis to select for plotting, colors,
            markers, linestyles and user defined parameters for the window
        """
        if fname == None:
            
            fname = str(QtGui.QFileDialog.getOpenFileName(
            self, 'Open settings file', './'))
            
        if fname:
            
            self.plot_window_settings = \
            self.widgets['InstrumentWidget'].load_settings(fname)
            
            self.instrument_connexion_setting_fname = fname

    def file_load_data(self):
        default_path = IOTool.get_config_setting("DATAFILE")
        if not default_path:
            default_path = './'
        fname = str(QtGui.QFileDialog.getOpenFileName(
            self, 'Open settings file', default_path))
        if fname:
            self.create_plw(fname)
            
    def file_print(self):
        self.current_pdw.print_figure(file_name=self.output_file.name)

    def option_display_debug_state(self):
        """Visualy let the user know the programm is in DEBUG mode"""

        self.setWindowIcon(QtGui.QIcon('images/icon_debug_py%s.png'%(PYTHON_VERSION)))
        self.setWindowTitle("-" * 3 + "DEBUG MODE" + "-" * 3 + " (python%s)"%(PYTHON_VERSION))
        self.setWindowOpacity(0.92)
        
    def option_display_normal_state(self):
        """Visualy let the user know the programm is in DEBUG mode"""
        self.setWindowIcon(QtGui.QIcon('images/icon_normal_py%s.png'%(PYTHON_VERSION)))
        self.setWindowTitle("LabGui (python%s)"%(PYTHON_VERSION))
        self.setWindowOpacity(1)

    def option_change_debug_state(self):
        """Togggle the debug state"""
        if self.DEBUG:
            self.option_display_normal_state()
            self.DEBUG = False
    
        else:
            self.option_display_debug_state()
            self.DEBUG = True
        
        self.refresh_ports_list()
        IOTool.set_config_setting(IOTool.DEBUG_ID,self.DEBUG,CONFIG_FILE)
        self.emit(SIGNAL("DEBUG_mode_changed(bool)"),self.DEBUG)
   
    def option_change_log_level(self):
        """change the file logging.conf's logging level"""
        
        log_level = str(self.sender().text())

        IOTool.set_config_setting("level", log_level, 
                                  os.path.join(ABS_PATH,"logging.conf"))
                                  
        logging.config.fileConfig(os.path.join(ABS_PATH,"logging.conf"))



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

    pdw.channel_objects["groupBox_X" ][1].setChecked(True)
    pdw.channel_objects["groupBox_Y" ][2].setChecked(True)
    pdw.channel_objects["groupBox_fit" ][2].setChecked(True)
    
    ex.toggle_DTT()
    
    #choose the linear fonction to fit
    ex.widgets['AnalyseDataWidget'].fitCombo.setCurrentIndex(2)
    ex.widgets['AnalyseDataWidget'].on_live_fitButton_clicked()
    
    ex.show()
    sys.exit(app.exec_())

def test_save_settings(idx = 0):
    """connect the Hub and save the settings"""
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()
    
    if idx == 0:
        ex.connect_instrument_hub()

    ex.file_save_settings("test_settings.set")    
    
    ex.show()
    sys.exit(app.exec_())
    
def test_load_settings(idx = 0):
    """load the settings and connect the Hub"""
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()
    
    ex.file_load_settings("test_settings.set")    
    
    if idx == 0:
        ex.connect_instrument_hub()
    
    elif idx == 1:
        #tries to load an unexisting file
        ex.file_load_settings("doesnt_exist_settings.set")
    
    ex.show()

    sys.exit(app.exec_())

def test_load_previous_data(data_path = os.path.join(ABS_PATH,'scratch','example_output.dat')):
    """
    open a new plot window with previous data
    """
    app = QtGui.QApplication(sys.argv)
    ex = LabGuiMain()

    ex.create_plw(data_path)

    ex.show()
    sys.exit(app.exec_())



if __name__ == "__main__":

#    launch_LabGui()
#    test_automatic_fitting()
#    test_load_previous_data()

#    test_save_settings(0)
    test_load_settings(1)
#    test_load_settings(0)


