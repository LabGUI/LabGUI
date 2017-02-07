# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 17:19:44 2013

Copyright (C) 10th april 2015 Benjamin Schmidt & Pierre-Francois Duc
License: see LICENSE.txt file
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

import LabDrivers.utils

from LabTools.IO import IOTool
from numpy import mod, array


class CommandWindow(QWidget):
    """This class operates the graphism of the instrument connectic"""
    # All the ports that can be used
    AVAILABLE_PORTS = []
    # Number of instrument that can be connected
    num_channels = 0
    color_set = ['cyan', 'black', 'blue', 'red', 'green',
                 'orange', 'magenta', 'maroon', 'plum', 'violet']

    def __init__(self, availiable_ports=["GPIB0::" + str(i) for i in range(30)], parent=None):
        super(CommandWindow, self).__init__(parent)

        self.AVAILABLE_PORTS = availiable_ports
        # Load the lists of instruments, with their parameters and their units
        [self.INSTRUMENT_TYPES, self.AVAILABLE_PARAMS,
            self.UNITS] = LabDrivers.utils.list_drivers()
        #print (IOTool.get_drivers_path())
        # This is a grid strictured layout
        self.grid = QGridLayout()
        # initilize the lists
        self.set_lists(-1)
        #self.resize(480, 600)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def __del__(self):
        print("exited command window")

    def set_lists(self, num_channels):
        """"This method is used to initialise a used defined number of lines of comboboxes, each line will hold information about one instrument"""

        if num_channels < 2 and num_channels > -1:
            num_channels = 2

        if num_channels == -1:
            first_init = True
            num_channels = 5

        else:
            first_init = False
            self.remove_all_lines()

        self.num_channels = num_channels
        # TickBoxes
        self.color_btn_list = []
        # Empty text boxes called Line Edit where the user can write which ever
        # title for plotting purposes
        self.param_name_le_list = []
        # Contains the names of the instruments' driver's modules
        self.instr_name_cbb_list = []
        # Contains the ports (GPIB/COM address) of the instruments
        self.port_cbb_list = []
        # Contains the lists of parameters of the instruments
        self.param_cbb_list = []

        # sets the headers for the buttons
        if self.num_channels > 0:
            self.headers = ["Color", "Name", "Type", "Instr", "Param"]
            for i, hdr_text in enumerate(self.headers):
                header = QLabel(hdr_text)
                self.grid.addWidget(header, 0, i)

            for i in range(self.num_channels):
                self.create_line(color=self.color_set[mod(i, 10)])

            if first_init:
                # create the button 'Connect' and adds it at the end of the
                # instrument list
                self.bt_connecthub = QtGui.QPushButton("Connect", self)
                self.bt_connecthub.setEnabled(True)
                self.connect(self.bt_connecthub, SIGNAL(
                    "clicked()"), self.bt_connecthub_clicked)
#                self.grid.addWidget(self.bt_connecthub, 0,3,1,1)

                self.bt_add_line = QtGui.QPushButton("Add item (doesn't work yet)", self)
                self.bt_add_line.setEnabled(False)
                self.connect(self.bt_add_line, SIGNAL(
                    "clicked()"), self.bt_add_line_clicked)
                    
                self.bt_remove_last = QtGui.QPushButton("Remove Last item", self)
                self.bt_remove_last.setEnabled(True)
                self.connect(self.bt_remove_last, SIGNAL(
                    "clicked()"), self.bt_remove_last_clicked)
                
                self.add_remove_layout = QHBoxLayout()
                self.add_remove_layout.addWidget(self.bt_add_line)
                self.add_remove_layout.addWidget(self.bt_remove_last)
                # set the layout and add a spacer bar

                self.vertical_layout = QVBoxLayout(self)
                self.vertical_layout.setObjectName("vertical_layout")
                self.vertical_layout.addWidget(self.bt_connecthub)
                self.vertical_layout.addLayout(self.grid)
                self.vertical_layout.addLayout(self.add_remove_layout)
                spacer_item = QSpacerItem(
                    20, 183, QSizePolicy.Minimum, QSizePolicy.Expanding)
                self.vertical_layout.addItem(spacer_item)

                self.setLayout(self.vertical_layout)
            else:
                pass
                # add the button 'Connect' at the end of the instrument list
#                self.grid.addWidget(self.bt_connecthub, self.num_channels+1,3,1,1)
                # this is an inside class defined function that clear all the
                # widgets on the windows as well as emptying the lists
        else:
            if first_init:
                pass
            else:
                self.resetLayout()

    def create_line(self, msg="", color=None):
        #        print "line created "+msg

        self.create_color_btn(self.color_btn_list, 0, color)
        self.create_lineedit(self.param_name_le_list, 1, label_text="dt(s)")
        self.create_combobox(
            "Instr name", self.instr_name_cbb_list, 2, label_text="Type")
        self.create_combobox("Port", self.port_cbb_list,
                             3, label_text="GPIB/COM Port")
        self.create_combobox("Param", self.param_cbb_list,
                             4, label_text="Measurement")

    def remove_lastline(self):
        # decrease the number of channels by one
        self.num_channels = self.num_channels - 1
        # group the different lists into one list to save space
        combo_array = [self.color_btn_list, self.param_name_le_list,
                       self.instr_name_cbb_list, self.port_cbb_list, self.param_cbb_list]
        # remove one widget from the lists and the layout
        for combo in combo_array:
            widget = combo[self.num_channels]
            combo.remove(widget)
            self.grid.removeWidget(widget)
            try:
                widget.setParent(None)
            except:
                pass
            widget.close()
        # move the button 'Connect' one line up
#        self.grid.removeWidget(self.bt_connecthub)
#        self.grid.addWidget(self.bt_connecthub, self.num_channels+1,3,1,1)

    def remove_all_lines(self):
        self.num_channels = 0
        try:
            self.grid.removeWidget(self.bt_connecthub)
        except:
            pass
        combo_array = [self.color_btn_list, self.param_name_le_list,
                       self.instr_name_cbb_list, self.port_cbb_list, self.param_cbb_list]
        # remove all the widgets from the lists and the layout
        for combo in combo_array:
            for wid in reversed(combo):
                combo.remove(wid)
                self.grid.removeWidget(wid)
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
        self.vertical_layout.addLayout(self.grid)
        self.vertical_layout.addLayout(self.add_remove_layout)


        #spacer_item = QSpacerItem(
       #     20, 183, QSizePolicy.Minimum, QSizePolicy.Expanding)
       # self.vertical_layout.addItem(spacer_item)

    def create_lineedit(self, le_list, col, label_text="Name"):
        index = len(le_list)
        le = QLineEdit(self)

        le.setObjectName("param_name_le_list " + str(index))
        self.connect(le, SIGNAL("textEdited(QString)"), self.lineEdit_handler)
        # add the newly created widget to the list and tothe layout
        le_list.append(le)
        le.insert(label_text)
        self.grid.addWidget(le, index + 1, col, 1, 1)

    def create_color_btn(self, color_btn_list, col, color):

        index = len(color_btn_list)

        if not color:
            color = self.color_set[mod(index, 10)]

        btn = QPushButton(self)
        btn.setObjectName("param_name_le_list " + str(index))
        btn.setStyleSheet('QPushButton {background-color: %s}' % color)
        btn.setFixedSize(20, 20)

        self.connect(btn, SIGNAL("clicked()"), self.color_btn_handler)
        # add the newly created widget to the list and tothe layout
        color_btn_list.append(btn)
        self.grid.addWidget(btn, index + 1, col, 1, 1)

    def create_tickbox(self, cb_list, col, label_text="Color"):
        # take the measure of the list length
        index = len(cb_list)
        cb = QCheckBox("", self)
        cb.setObjectName("checkBox " + str(index))
        self.connect(cb, SIGNAL("stateEdited(int)"), self.tickbox_handler)
        # add the newly created widget to the list and tothe layout
        cb_list.append(cb)
        self.grid.addWidget(cb, index + 1, col, 1, 1)

    def create_combobox(self, name, cbb_list, col, label_text="label"):
        index = len(cbb_list)
        cbb = QComboBox(self)
        cbb.setObjectName("comboBox " + name + " " + str(index))
        cbb.setStyleSheet(
            "QComboBox::drop-down {border-width: 0px;} QComboBox::down-arrow {image: url(noimg); border-width: 0px;}")
        if name == 'Instr name':
            cbb.addItems(self.INSTRUMENT_TYPES)
            cbb.setCurrentIndex(cbb.findText("TIME"))
            self.connect(cbb, SIGNAL("currentIndexChanged(int)"),
                         self.combobox_handler)
        if name == 'Port':
            cbb.addItems(self.INSTRUMENT_TYPES)
            cbb.setCurrentIndex(cbb.findText("TIME"))
#            self.connect(cbb, SIGNAL("activated(int)"), self.combobox_dev_port_handler)
        if name == "Param":
            cbb.addItems(self.AVAILABLE_PARAMS['TIME'])
            cbb.setCurrentIndex(cbb.findText("dt"))
            self.connect(cbb, SIGNAL("currentIndexChanged(int)"),
                         self.combobox_unit_handler)

        # add the newly created widget to the list and tothe layout
        cbb_list.append(cbb)
        self.grid.addWidget(cbb, index + 1, col, 1, 1)

    def combobox_handler(self):
        """update the port list and the parameter list upon the (de)selection of an instrument from a combobox"""
        # find on which line the user changed the combobox
        box_index = self.instr_name_cbb_list.index(self.sender())
        # select the items on the line corresponding to the same instrument
        instr_box = self.instr_name_cbb_list[box_index]
        port_box = self.port_cbb_list[box_index]
        param_box = self.param_cbb_list[box_index]

        # empty the port_list combobox
        for i in range(port_box.count() + 1):
            port_box.removeItem(0)

        instr_name = instr_box.currentText()
        if instr_name == "TIME":
            port_box.clear()
            # it will not remove last line if there are only two
            if box_index == self.num_channels - 2 and self.num_channels > 2:
                # if this is the last one of the list then remove it, only if
                # the one before is also a TIME
                if self.instr_name_cbb_list[box_index + 1].currentText() == "TIME":
                    self.remove_lastline()
        elif instr_name == "FridgeClient":
            port_box.clear()
        else:
            # One could think of a solution for writing only the port that are
            # still availiable
            port_box.clear()
            port_box.addItems(self.AVAILABLE_PORTS)
            # if this is the last one of the list then add a combobox into the
            # list
            if box_index + 1 == self.num_channels:
                # move the button 'Connect' after the newly created line
                #                self.grid.removeWidget(self.bt_connecthub)
                self.create_line("ici")
                self.num_channels = self.num_channels + 1
#                self.grid.addWidget(self.bt_connecthub, self.num_channels+2,3,1,1)
        param_box.clear()
        param_box.addItems(self.AVAILABLE_PARAMS[str(instr_name)])

        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'
        self.bt_connecthub.setEnabled(True)

    def combobox_dev_port_handler(self):
        """sets the connect button enabled"""
        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'
        self.bt_connecthub.setEnabled(True)

    def combobox_unit_handler(self):
        """update the lineEdit with unit corresponding to the instrument parameter upon its selection"""
        # find on which line the user changed the combobox
        box_index = self.param_cbb_list.index(self.sender())
        # select the items on the line corresponding to the same instrument
        le = self.param_name_le_list[box_index]
        instr = self.instr_name_cbb_list[box_index].currentText()
        instr_params = self.AVAILABLE_PARAMS[str(instr)]

        current_param = self.param_cbb_list[box_index].currentText()
        label = str(le.text())
        label = label.split('(')[0]

        # if there is no existing label it puts the param name
        if label == "":
            label = current_param

        # if there is no user define param name different from the instrument params
        # it puts the correct param name
        if label in self.UNITS:
            label = current_param
        le.setText(label + self.get_unit(box_index))

        # After changes the user should be able to update the instrumentHub by
        # clicking on the button 'Connect'
        self.bt_connecthub.setEnabled(True)

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
        self.emit(SIGNAL("labelsChanged()"))

    def color_btn_handler(self):
        btn = self.sender()
        idx = self.color_btn_list.index(btn)

        color = QColorDialog.getColor(initial=btn.palette().color(1))
        btn.setStyleSheet('QPushButton {background-color: %s}' % color.name())
        print(self.get_color_list())
        self.emit(SIGNAL("colorsChanged()"))

    def tickbox_handler(self):
        print(self.collect_device_info())
        # this would take action upon tickbox change
#        pass

    def bt_connecthub_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_connecthub.isEnabled:
            self.emit(SIGNAL("ConnectInstrumentHub(bool)"), True)

    def bt_add_line_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_remove_last.isEnabled:
            self.create_line()
            #self.emit(SIGNAL("ConnectInstrumentHub(bool)"), True)
            
    def bt_remove_last_clicked(self):
        """when this method is called (upon button 'Connect' interaction) it send a signal, which will be treated in the main window"""
        if self.bt_remove_last.isEnabled:
            self.remove_lastline()
            #self.emit(SIGNAL("ConnectInstrumentHub(bool)"), True)
            
    def collect_device_info(self):
        """gather the text displayed in the comboboxes"""

        combo_array = [self.instr_name_cbb_list,
                       self.port_cbb_list, self.param_cbb_list]
        device_info = [[], [], []]

        for i, combo in enumerate(combo_array):
            for p in combo:
                device_info[i].append(str(p.currentText()))
#                print p,str(p.currentText())
        return device_info

    def get_label_list(self):
        return [str(le.text()) for le in self.param_name_le_list]

    def get_cbb_string_list(self, cbb_list):
        return [str(cbb.currentText()) for cbb in cbb_list]

    def get_descriptor_list(self):

        name_list = self.get_cbb_string_list(self.instr_name_cbb_list)
        port_list = self.get_cbb_string_list(self.port_cbb_list)
        param_list = self.get_cbb_string_list(self.param_cbb_list)

        output = []
        for [name, port, param] in zip(name_list, port_list, param_list):
            output.append(name + '[' + port + '].' + param)

        return output

    def get_color_list(self):
        return [str(btn.palette().color(1).name()) for btn in self.color_btn_list]

    def load_settings(self, fname):
        """ Load in instrument and initial plot settings from a file"""
        try:
            settings_file = open(fname)
            idx = 0
#            print self.AVAILABLE_PORTS
#            print self.INSTRUMENT_TYPES
            self.remove_all_lines()

            for li in self.param_name_le_list:
                li.setText('')

#            self.grid.removeWidget(self.bt_connecthub)

            for line in settings_file:

                #            print line
                # file format is comma-separated list of settings for each
                # channel
                line = line.strip()
                settings = line.split(',')

                if settings[0] and settings[0] != 'CALC':
                    self.num_channels = self.num_channels + 1
                    self.create_line()
                    self.param_name_le_list[idx].setText(settings[0])
                    instr_type = settings[1].strip()
    #                print instr_type

                    if instr_type in self.INSTRUMENT_TYPES:
                        # set the index to the index corresponding to the instrument
                        # type (found using the findtext function)
                        self.instr_name_cbb_list[idx].setCurrentIndex(
                            self.instr_name_cbb_list[idx].findText(instr_type))

                        if instr_type == "TIME":
                            #                        print "time " + str(idx)
                            self.port_cbb_list[idx].clear()
                        else:
                            port = settings[2].strip().upper()
    #                        print instr_type,port
    #                        print str(idx)
    #                        print port in self.AVAILABLE_PORTS
                            # if the port appears to be valid, select it in the box
                            # otherwise add it, but show an icon indicating the
                            # problem
                            if port in self.AVAILABLE_PORTS:
                                self.port_cbb_list[idx].setCurrentIndex(
                                    self.port_cbb_list[idx].findText(port))
    #                            print port
    #                            print self.port_cbb_list[idx].findText(port)
                            else:
                                print(instr_type)
                                self.port_cbb_list[idx].addItem(
                                    QIcon("not_found.png"), port)
                                self.port_cbb_list[idx].setCurrentIndex(
                                    self.instr_name_cbb_list[idx].count() - 1)

                        self.param_cbb_list[idx].clear()
                        self.param_cbb_list[idx].addItems(
                            self.AVAILABLE_PARAMS[instr_type])

                        param = settings[3].strip()
                        if param in self.AVAILABLE_PARAMS[instr_type]:
                            self.param_cbb_list[idx].setCurrentIndex(
                                self.param_cbb_list[idx].findText(param))
                    idx += 1
            settings_file.close()
            self.remove_lastline()
#            self.grid.addWidget(self.bt_connecthub, self.num_channels+2,3,1,1)
            self.emit(SIGNAL("colorsChanged()"))
        except:
            print("Setting file loading error, the filename was :", fname)

    def save_settings(self, fname):
        """Generates a settings file that can be read with load_settings."""
        settings_file = open(fname, 'w')
        print("Settings saved in " + fname)
        for idx in range(self.num_channels):
            settings_file.write(self.param_name_le_list[idx].text() + ', ')
            settings_file.write(self.instr_name_cbb_list[
                                idx].currentText() + ', ')
            settings_file.write(self.port_cbb_list[idx].currentText() + ', ')
            settings_file.write(self.param_cbb_list[idx].currentText() + ', ')
            settings_file.write('\n')
        settings_file.close()

    def get_unit(self, channel):
        answer = ""
        if channel < self.num_channels:
            param = self.param_cbb_list[channel].currentText()
            try:
                answer = "(" + self.UNITS[str(param)] + ")"
            except:
                answer = ""
        return answer
if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = CommandWindow()
    ex.show()

#    ex.remove_all_lines()
    sys.exit(app.exec_())
