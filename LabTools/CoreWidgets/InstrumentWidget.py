# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 17:19:44 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file
"""
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import SIGNAL, Qt
import sys
import PyQt4.QtGui as QtGui
from types import MethodType


import LabDrivers.Tool as Tool
import LabDrivers.utils
from LabTools.Display.PlotPreferences import color_blind_friendly_colors

import logging


width_instr = 100
width_port = 130
width_param = 80

class SingleLineWidget(QtGui.QWidget):
    AVAILABLE_PORTS = []
    # Number of instrument that can be connected
    num_channels = 0
    color_set = color_blind_friendly_colors(10)
       
    # I'm thinking of modifying the design of the CommandWindow so that it just has a set of this object instead of the many different arrays of cbb to take care of.
    def __init__(self, available_ports=["GPIB0::" + str(i) for i in range(30)], color = None, parent=None):    
        super(SingleLineWidget, self).__init__(parent)
        
        self.AVAILABLE_PORTS = available_ports
        # Load the lists of instruments, with their parameters and their units
        [self.INSTRUMENT_TYPES, self.AVAILABLE_PARAMS,
            self.UNITS] = LabDrivers.utils.list_drivers()
            
        # TickBoxes
        self.color_btn = self.create_color_btn(color)
        # Empty text boxes called Line Edit where the user can write which ever
        # title for plotting purposes
        self.param_name_le= self.create_lineedit(label_text="dt(s)")
        # Contains the names of the instruments' driver's modules
        self.instr_name_cbb = self.create_combobox("Instr name", label_text="Type")
        # Contains the ports (GPIB/COM address) of the instruments
        self.port_cbb = self.create_combobox("Port", label_text="GPIB/COM Port")
        
        # Contains the lists of parameters of the instruments
        self.param_cbb = self.create_combobox("Param", label_text="Measurement")
        
        self.horizontal_layout = QtGui.QHBoxLayout(self)
#        self.horizontal_layout.addWidget(self.color_btn)
        self.horizontal_layout.addWidget(self.param_name_le)
        self.horizontal_layout.addWidget(self.instr_name_cbb)       
        self.horizontal_layout.addWidget(self.port_cbb)
        self.horizontal_layout.addWidget(self.param_cbb)
        
        self.setLayout(self.horizontal_layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.horizontal_layout.setContentsMargins(0,0,0,0)
        
        
    def create_lineedit(self, label_text="Name"): 
        le = QtGui.QLineEdit(self)

        le.setObjectName("param_name_le")
        self.connect(le, SIGNAL("textEdited(QString)"), self.lineEdit_handler)
        # add the newly created widget to the list and tothe layout
        le.insert(label_text)

        return le

    def create_color_btn(self, color):

#        if color == None:
#            color = self.color_set[mod(index, 10)]

        btn = QtGui.QPushButton(self)
        btn.setObjectName("param_name_le")
        if not color == None:
            btn.setStyleSheet('QPushButton {background-color: %s}' % color)
        btn.setFixedSize(20, 20)

        self.connect(btn, SIGNAL("clicked()"), self.color_btn_handler)
        # add the newly created widget to the list and tothe layout
        return btn
        
    def create_tickbox(self, label_text="Color"):
        # take the measure of the list length
#        index = len(cb_list)
        cb = QtGui.QCheckBox("", self)
        cb.setObjectName("checkBox")
        self.connect(cb, SIGNAL("stateEdited(int)"), self.tickbox_handler)
        # add the newly created widget to the list and to the layout
        
        return cb

    def create_combobox(self, name, label_text="label"):
        cbb = QtGui.QComboBox(self)
        cbb.setObjectName("comboBox")
        cbb.setStyleSheet(
            "QComboBox::drop-down {border-width: 0px;} QComboBox::down-arrow {image: url(noimg); border-width: 0px;}")
        if name == 'Instr name':
            cbb.addItems(self.INSTRUMENT_TYPES)
            cbb.setCurrentIndex(cbb.findText("TIME"))
            self.connect(cbb, SIGNAL("currentIndexChanged(int)"),
                         self.combobox_handler)
            cbb.setFixedWidth(width_instr)                         
        if name == 'Port':
            
            #when creating a line the instrument TIME comes first so there is no port to connect to it
            cbb.addItem("")
  
#            self.connect(cbb, SIGNAL("activated(int)"), self.combobox_dev_port_handler)
            cbb.setFixedWidth(width_port)            
        if name == "Param":
            cbb.addItems(self.AVAILABLE_PARAMS['TIME'])
            cbb.setCurrentIndex(cbb.findText("dt"))
            self.connect(cbb, SIGNAL("currentIndexChanged(int)"),
                         self.combobox_unit_handler)
            cbb.setFixedWidth(width_param*1.5) 
        return cbb

    def combobox_handler(self):
        """update the port list and the parameter list upon the (de)selection of an instrument from a combobox"""

        # select the items on the line corresponding to the same instrument
#        instr_box = self.instr_name_cbb
#        port_box = self.port_cbb
#        param_box = self.param_cbb

        instr_name = str(self.instr_name_cbb.currentText())
        # One could think of a solution for writing only the port that are
        # still available
        self.port_cbb.clear()
        if instr_name == "TIME":
            self.port_cbb.addItem("")
        else:
            self.port_cbb.addItems(self.AVAILABLE_PORTS)

        self.param_cbb.clear()
        self.param_cbb.addItems(self.AVAILABLE_PARAMS[instr_name])
        
        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'
        
        # emit signal to say something was modified
        self.emit(SIGNAL("lineChanged()"))

    def combobox_dev_port_handler(self):
        """sets the connect button enabled"""
        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'
        self.emit(SIGNAL("lineChanged()"))

    def combobox_unit_handler(self):
        """update the lineEdit with unit corresponding to the instrument parameter upon its selection"""

        # select the items on the line corresponding to the same instrument
        le = self.param_name_le
        instr = self.instr_name_cbb.currentText()
        instr_params = self.AVAILABLE_PARAMS[str(instr)]

        current_param = self.param_cbb.currentText()
        label = str(le.text())
        label = label.split('(')[0]

        # if there is no existing label it puts the param name
        if label == "":
            label = current_param

        # if there is no user define param name different from the instrument params
        # it puts the correct param name
        if label in self.UNITS:
            label = current_param
        le.setText(label + self.get_unit())

        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'

        self.emit(SIGNAL("lineChanged()"))
        
    def lineEdit_handler(self, string):
        #        print string
        # find on which line the user edited the lineEdit
        # this code was really buggy and made it hard to type useful labels
        # commented out for now.
        #        box_index=self.param_name_le_list.index(self.sender())
        #        current_param=self.param_cbb_list[box_index].currentText()
        #        le=self.param_name_le_list[box_index]
        #        label=str(le.text())
        #        #if the label is not of the format 'param_name'('unit_name')
        #        if not label.rfind(')')==len(label)-1:
        #            #for the case ('unit_name')'param_name'->'param_name'('unit_name')
        #            if label[0]=='(':
        #                label=label[3:len(label)]
        #            ##for the case 'param_name1'('unit_name')'param_name2'->'param_name1''param_name2'('unit_name')
        #            else:
        #                label=label[0:label.rfind('(')]+label[label.rfind(')')+1:len(label)]
        #        else:
        #            #take the ('unit_name') out
        #            label=label.split('(')[0]
        #
        #        #if the label is to be empty it will be replaced by the parameter name
        #        if label=="":
        #            label=current_param
        #        #reassamble 'param_name'('unit_name')
        #        le.setText(label+self.get_unit(box_index))
        self.emit(SIGNAL("lineChanged()"))

    def color_btn_handler(self):
        logging.debug("triggered")
        btn = self.sender()
#        idx = self.color_btn_list.index(btn)

        color = QtGui.QColorDialog.getColor(initial=btn.palette().color(1))
        btn.setStyleSheet('QPushButton {background-color: %s}' % color.name())
#        print self.get_color_list()
        #emit the signal (Labgui will catch it and transfer it to the various windows which need to update their colors)
        self.emit(SIGNAL("colorChanged()"))

    def tickbox_handler(self):
        logging.debug("triggered")
#        print self.collect_device_info()
        # this would take action upon tickbox change
        
    def get_unit(self):
        answer = ""
        param = self.param_cbb.currentText()
        try:
            answer = "(" + self.UNITS[str(param)] + ")"
        except:
            answer = ""
        return answer        

    def collect_device_info(self):
        """gather the text displayed in the comboboxes"""

        device_info  =[]

        for p in [self.instr_name_cbb, self.port_cbb, self.param_cbb]:
            device_info.append(str(p.currentText()))

        return device_info

    def get_descriptor(self):

        name = str(self.instr_name_cbb.currentText())
        port = str(self.port_cbb.currentText())
        param = str(self.param_cbb.currentText())

        return name + '[' + port + '].' + param

    def refresh_port_cbb(self,port_list = None):
        """run a function from Tool module which list the available ports into the combobox"""
        if port_list == None:
            self.AVAILABLE_PORTS = Tool.refresh_device_port_list()
        else:
            self.AVAILABLE_PORTS = port_list
        self.port_cbb.clear()
        instr_name = str(self.instr_name_cbb.currentText())
        if instr_name == "TIME":
            self.port_cbb.addItem("")
        else:
            self.port_cbb.addItems(self.AVAILABLE_PORTS)

    def set_color(self,color=None):
        if not color == None:
            self.color_btn.setStyleSheet('QPushButton {background-color: %s}' % color)
        
    def get_color(self):
        return str(self.color_btn.palette().color(1).name())
    
    def get_label(self):
        return self.param_name_le.text()


class InstrumentWindow(QtGui.QWidget):
    """This class operates the graphism of the instrument connectic"""
    # All the ports that can be used
    AVAILABLE_PORTS = []
    # Number of instrument that can be connected
    # from now on, use len(lines) instead of self.num_channels
    #num_channels = 0
    color_set = color_blind_friendly_colors(10)

    def __init__(self, parent = None, 
                 available_ports = ["GPIB0::" + str(i) for i in range(30)],
                 debug = False):
        super(InstrumentWindow, self).__init__(parent)


#        print "available ports inside InstrumentWindows",available_ports        
        
        self.DEBUG = debug

        self.AVAILABLE_PORTS = available_ports
        # Load the lists of instruments, with their parameters and their units
        [self.INSTRUMENT_TYPES, self.AVAILABLE_PARAMS,
            self.UNITS] = LabDrivers.utils.list_drivers()
        #print (IOTool.get_drivers_path())
        # This is a grid strictured layout
        self.line_layout = QtGui.QVBoxLayout()
        # initilize the lists
        # all the widgets of time SingleLineWidget will go in this list.
        self.lines = []
        self.set_lists(-1)
        #self.resize(480, 600)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def __del__(self):
        logging.debug("exited Instrument  window")

    def set_lists(self, num_channels):
        """"This method is used to initialise a user defined number of lines of comboboxes, each line will hold information about one instrument"""

        if num_channels < 2 and num_channels > -1:
            num_channels = 2

        if num_channels == -1:
            first_init = True
            num_channels = 5

        else:
            first_init = False
            self.remove_all_lines()
        #self.num_channels = num_channels
        # sets the headers for the buttons
        if num_channels > 0:
            self.headers = ["Color", "Name", "Instr", "Port", "Param"]
            widths = [None, None,width_instr, width_port, width_param]
            self.header_layout = QtGui.QHBoxLayout()
            for i, hdr_text in enumerate(self.headers):
                header = QtGui.QLabel(hdr_text)
                if widths[i]:
                    header.setFixedWidth(widths[i])
                self.header_layout.addWidget(header)
            self.line_layout.addLayout(self.header_layout)
            
            
            for i in range(num_channels):
                self.create_line()

            if first_init:
                # create the button 'Connect' and adds it at the end of the
                # instrument list
                self.bt_connecthub = QtGui.QPushButton("Connect", self)
                self.bt_connecthub.setEnabled(True)
                self.connect(self.bt_connecthub, SIGNAL(
                    "clicked()"), self.bt_connecthub_clicked)
                
#                self.bt_refreshports = QtGui.QPushButton("RefreshPorts", self)
#                self.bt_refreshports.setEnabled(True)
#                self.connect(self.bt_refreshports, SIGNAL(
#                    "clicked()"), self.bt_refreshports_clicked)
#                self.line_layout.addWidget(self.bt_connecthub, 0,3,1,1)

                self.bt_add_line = QtGui.QPushButton("Add item", self)
                self.bt_add_line.setEnabled(True)
                self.connect(self.bt_add_line, SIGNAL(
                    "clicked()"), self.bt_add_line_clicked)
                    
                self.bt_remove_last = QtGui.QPushButton("Remove last item", self)
                self.bt_remove_last.setEnabled(True)
                self.connect(self.bt_remove_last, SIGNAL(
                    "clicked()"), self.bt_remove_last_clicked)
                
                self.add_remove_layout = QtGui.QHBoxLayout()
                self.add_remove_layout.addWidget(self.bt_add_line)
                self.add_remove_layout.addWidget(self.bt_remove_last)
                # set the layout and add a spacer bar

                self.vertical_layout = QtGui.QVBoxLayout(self)
                self.vertical_layout.setObjectName("vertical_layout")
                self.vertical_layout.addWidget(self.bt_connecthub)
                self.vertical_layout.addLayout(self.line_layout)
                self.vertical_layout.addLayout(self.add_remove_layout)
                spacer_item = QtGui.QSpacerItem(
                    20, 183, QSizePolicy.Minimum, QSizePolicy.Expanding)
                self.vertical_layout.addItem(spacer_item)

                self.setLayout(self.vertical_layout)
            else:
                pass
                # add the button 'Connect' at the end of the instrument list
#                self.line_layout.addWidget(self.bt_connecthub, self.num_channels+1,3,1,1)
                # this is an inside class defined function that clear all the
                # widgets on the windows as well as emptying the lists
        else:
            if first_init:
                pass
            else:
                self.resetLayout()

    def create_line(self, msg="", color=None):
        
                
        self.color_set = color_blind_friendly_colors(len(self.lines)+1)
#        if color==None:
#            self.color_set = color_blind_friendly_colors(len(self.lines)+1)
#            color = self.color_set[-1]
        
#        print 'line created'
        new_line = SingleLineWidget(self.AVAILABLE_PORTS)
        self.lines.append(new_line)
        self.line_layout.addWidget(new_line)
        for line,color in zip(self.lines,self.color_set):
            line.set_color(color)
        self.connect(new_line, SIGNAL(
                    "lineChanged()"), self.lines_changed)
        self.connect(new_line, SIGNAL("colorChanged()"), self.update_colors)

        self.update_colors()
        return new_line

    def remove_lastline(self):
        # decrease the number of channels by one
        widget = self.lines[-1]
        self.lines.remove(widget)
        self.line_layout.removeWidget(widget)
        try:
            widget.setParent(None)
        except:
            pass
        widget.close()
        self.color_set = color_blind_friendly_colors(len(self.lines))
        for line,color in zip(self.lines,self.color_set):
            line.set_color(color)
        logging.debug('line removed')
        # move the button 'Connect' one line up
#        self.line_layout.removeWidget(self.bt_connecthub)
#        self.line_layout.addWidget(self.bt_connecthub, self.num_channels+1,3,1,1)

    def remove_all_lines(self):
        self.num_channels = 0
        try:
            self.line_layout.removeWidget(self.bt_connecthub)
        except:
            pass
        for wid in reversed(self.lines):
            self.lines.remove(wid)
            self.line_layout.removeWidget(wid)
            wid.close()

    def resetLayout(self):
        # delete the grid and the spacer
        for i in reversed(list(range(self.vertical_layout.count()))):
            item = self.vertical_layout.itemAt(i)
#            print item
            self.vertical_layout.removeItem(item)
            try:
                item.setParent(None)
            except:
                pass
        # add the new grid and a spacer
        self.vertical_layout.addWidget(self.bt_connecthub)
        self.vertical_layout.addLayout(self.line_layout)
        self.vertical_layout.addLayout(self.add_remove_layout)


        #spacer_item = QSpacerItem(
       #     20, 183, QSizePolicy.Minimum, QSizePolicy.Expanding)
       # self.vertical_layout.addItem(spacer_item)

    
#        pass
    

    def lines_changed(self):
        """if any line is changed the color of the connect button is changed so that one can notice """
        self.bt_connecthub.setStyleSheet("background-color : Window")

    def update_colors(self):
        """this simply send the triggered signal from a Single line instance to the LabGui instance (and any other listeners)"""
        self.emit(SIGNAL("colorsChanged()"))
        
    def bt_connecthub_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_connecthub.isEnabled:

            self.bt_connecthub.setStyleSheet("background-color : '#b3e0ff'")

            self.emit(SIGNAL("ConnectInstrumentHub(bool)"), True)

    def bt_add_line_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_remove_last.isEnabled:
            self.create_line()
            self.emit(SIGNAL("AddedInstrument(bool)"), True)
            # the lines have changed - call the relevant function!            
            self.lines_changed()           
            
    def bt_remove_last_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_remove_last.isEnabled:
            self.remove_lastline()
            self.emit(SIGNAL("RemovedInstrument(bool)"), True)
            # the lines have changed - call the relevant function!            
            self.lines_changed()    
            
    def collect_device_info(self):
        """gather the text displayed in the comboboxes"""

        device_info = [[], [], []]

        for line in self.lines:
            for i, p  in enumerate([line.instr_name_cbb, line.port_cbb, line.param_cbb]):
                device_info[i].append(str(p.currentText()))
#                print p,str(p.currentText())
        return device_info

    def get_label_list(self):
        return [line.get_label() for line in self.lines]


    def get_descriptor_list(self):
        output = []
        for line in self.lines:
            output.append(line.get_descriptor())

        return output

    def get_color_list(self):
        return [line.get_color() for line in self.lines]
        
    def refresh_cbb_port(self):
        """run a method from SingleLine class which refresh the availiable ports"""
        
        self.AVAILABLE_PORTS = Tool.refresh_device_port_list()
        for line in self.lines:
            line.refresh_port_cbb(self.AVAILABLE_PORTS)

    def load_settings(self, fname):
        """ Load in instrument and initial plot settings from a file"""

        try:
            
            settings_file = open(fname,'r')
        
        except IOError:
            
            print("No such file exists : %s"%(fname))

        #the new settings will overwrite existing ones
        self.remove_all_lines()

        window_settings = []

        for setting_line in settings_file:
            
            # file format is comma-separated list of settings for each channel
            setting_line = setting_line.strip()
            settings = setting_line.split(',')
            
            if settings[0] and settings[0] != 'CALC':
                
                logging.debug(setting_line)
                
                new_line = self.create_line()
                
                param_name = settings[0].strip()
    
                new_line.param_name_le.setText(param_name)                
                

                
                
                # For backwards compatibility with old settings files, leave 
                # this part in.
                # The TIME module was renamed because there is
                # already the built-in time module

                instr_type = settings[1].strip()

                if instr_type == 'TIME':
                    instr_type == 'Internal'

                
                if not instr_type in self.INSTRUMENT_TYPES:
                    
                     logging.warning("No module for %s available"%(instr_type))
                     
                else:
                    
                    # set the index to the index corresponding to the instrument
                    # type (found using the findtext function)
                    new_line.instr_name_cbb.setCurrentIndex(
                        new_line.instr_name_cbb.findText(instr_type))

                    if instr_type == "Internal":
                        
                        new_line.port_cbb.clear()
                        new_line.port_cbb.addItem('Internal')
                        
                    else:
                        
                        port = settings[2].strip().upper()

                        # if the port appears to be valid, select it in the box
                        # otherwise add it, but show an icon indicating the
                        # problem
                        if port in self.AVAILABLE_PORTS:
                            
                            new_line.port_cbb.setCurrentIndex(
                                new_line.port_cbb.findText(port))

                        else:
                            
                            if not self.DEBUG:
                                
                                logging.warning("the port %s is not available,\
 please check your connectic or your settings file\n"%(port))

                    #fills the parameter combobox with instrument parameters
                    new_line.param_cbb.clear()
                    new_line.param_cbb.addItems(
                        self.AVAILABLE_PARAMS[instr_type])
                        
                    #modify the parameter combobox with the chosen parameter
                    param = settings[3].strip()

                    if param in self.AVAILABLE_PARAMS[instr_type]:
                        new_line.param_cbb.setCurrentIndex(
                            new_line.param_cbb.findText(param))
                            
            #collect the settings for the window    
            window_settings.append([s.strip().replace("'",'') 
                                    for s in settings[4:]])
            
        settings_file.close()

        self.emit(SIGNAL("colorsChanged()"))
        
        return window_settings

    def save_settings(self, fname, window_settings):
        """Generates a settings file that can be read with load_settings."""
        settings_file = open(fname, 'w')
        logging.info("Settings saved in " + fname)
        
        #write the text of each line object into a line of text file
        for i, line in enumerate(self.lines):
            
            #the user defined labels
            settings_file.write(line.get_label() + ', ')
            
            #the connection device ports, instrument and parameter names
            device_info = line.collect_device_info()
            n_info = len(device_info)
            
            for j,item in enumerate(device_info):
                
                if j  == n_info - 1:
                    
                    settings_file.write(item)
                
                else:
                
                    settings_file.write(item + ', ')
                
            #if available, the plot window ticks for axes
            try:
                
                settings_file.write(window_settings[i])
                
            except IndexError:
                
                logging.info(
                "Couldn't save the plot window information to the file %s"
                %(fname))
                
            settings_file.write('\n')
            
        settings_file.close()


def refresh_ports_list(parent):
    """Update the availiable port list in the InstrumentWindow module """

    parent.widgets['InstrumentWidget'].refresh_cbb_port()


def connect_instrument_hub(parent, signal = True):
    """
        When the button "Connect" is clicked this method actualise the InstrumentHub
        according to what the user choosed in the command window. 
        It cannot change while the DataTaker is running though
    """
    #@ISSUE
    # I should add something here to avoid that we reconnect the instrument hub if the # of instrument is different
    # and also not allow to take data if the current file header doesn't
    # correspond to the intrument hub   

    if signal:
        
        [instr_name_list, dev_list, param_list] = parent.collect_instruments()
        logging.debug([instr_name_list, dev_list, param_list])
        
        actual_instrument_number = len(
            parent.instr_hub.get_instrument_list())
        cmdwin_instrument_number = len(instr_name_list)
        
        # if the datataker is running the user should not modify the length
        # of the instrument list and connect it
        connect = False
        
        if parent.isrunning():
            
            if actual_instrument_number == cmdwin_instrument_number or \
               actual_instrument_number == 0:
                   
                connect = True
                
        else:
            
            connect = True

        if connect:
            
            print("Connect instrument hub...")
            parent.instr_hub.connect_hub(
                instr_name_list, dev_list, param_list)
            print("...instrument hub connected")
            parent.emit(
                SIGNAL("instrument_hub_connected(PyQt_PyObject)"), param_list)
        
        else:
            
            print()
            logging.warning("You cannot connect a number of instrument \
different than " + str(actual_instrument_number) 
+ " when the datataker is running")
            print()

        logging.debug("The instrument list : " \
                      + str(parent.instr_hub.get_instrument_list()))
                      
        #show a plot by default
        parent.create_pdw()
        
        parent.actual_pdw = parent.get_last_window()



def connect_instrument(parent, connection_param):
    """
        When the button "Connect" is clicked this method actualise the InstrumentHub
        according to what the user choosed in the command window. 
        It cannot change while the DataTaker is running though
    """
    [instr_name, dev_port, param] = connection_param

#        cmdwin_instrument_number=len(instr_name_list)
    # if the datataker is running the user should not modify the length of
    # the instrument list and connect it
    connect = False
    if parent.isrunning():
        print("As data are being recorded now, you are not allowed to connect "\
              + instr_name + " to " + dev_port)
#            if actual_instrument_number == cmdwin_instrument_number or actual_instrument_number==0:
#                connect=True
    else:
        connect = True

    actual_instrument_number = len(parent.instr_hub.get_instrument_list())
    print("number of instruments connected (b)", actual_instrument_number)
    
    if connect:
        
        print("Connect single instrument...")
        parent.instr_hub.connect_instrument(instr_name, dev_port, param)
        print("...single instrument connected")
#«            self.emit(SIGNAL("instrument_hub_connected(PyQt_PyObject)"),None)
    else:
        
        print()
        
        print("You cannot connect a number of instrument different than " + \
        str(actual_instrument_number) + " when the datataker is running")
        
        print()
        
    actual_instrument_number = len(parent.instr_hub.get_instrument_list())
    print("number of instruments connected (a)", actual_instrument_number)


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain
    
    create a QDock widget and store a reference to the widget
    """    

    mywidget = InstrumentWindow(parent = parent)  
    
    parent.instrument_connexion_setting_fname=""  
    
    #create a QDockWidget        
    instDockWidget = QtGui.QDockWidget("Instrument Setup", parent)
    instDockWidget.setObjectName("InstDockWidget")
    instDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
    #make is possible to scroll up and down
    instScrollArea = QtGui.QScrollArea()
    instScrollArea.setWidgetResizable(True)
    instScrollArea.setEnabled(True)
    
    #instScrollArea.setMaximumSize(375, 300)  # optional
    
    instScrollArea.setWidget(mywidget)
    
    instDockWidget.setWidget(instScrollArea)
    parent.addDockWidget(Qt.RightDockWidgetArea, instDockWidget)
    
    
    #fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['InstrumentWidget'] = mywidget
    
    parent.refresh_ports_list()      
    
    #Enable the toggle view action
    parent.windowMenu.addAction(instDockWidget.toggleViewAction())

    #add a series of signals tiggers


    parent.connect_instrument_hub = MethodType(connect_instrument_hub,
                                               parent, parent.__class__)    
        
    
    parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
            "ConnectInstrumentHub(bool)"), parent.connect_instrument_hub) 


    parent.connect_instrument = MethodType(connect_instrument,
                                               parent, parent.__class__)


    parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
        "ConnectInstrument(PyQt_PyObject)"), parent.connect_instrument)
        
    
    parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
        "colorsChanged()"), parent.update_colors)
        
    parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
        "labelsChanged()"), parent.update_labels)
        
            
     
def test_load_settings():
    app = QtGui.QApplication(sys.argv)
    ex = InstrumentWindow(debug = True)

    print ex.load_settings("C:\\Users\\pfduc\\Documents\\labgui_github\\test_settings.set")
    ex.show()

    sys.exit(app.exec_())

def test_main():
    app = QtGui.QApplication(sys.argv)
    listi = Tool.refresh_device_port_list()
    ex = InstrumentWindow(debug = True)
    ex.refresh_cbb_port(listi)
#    ex.load_settings('C:\Users\pfduc\Documents\g2gui\g2python\settings\demo_dice.txt')
    #ex = SingleLineWidget()
#    ex.save_settings("test_save.txt")
    ex.show()

#    ex.remove_all_lines()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import logging.config
    import os
    ABS_PATH = "C:\\Users\\pfduc\\Documents\\labgui_github"
    logging.config.fileConfig(os.path.join(ABS_PATH,"logging.conf"))

    test_load_settings()