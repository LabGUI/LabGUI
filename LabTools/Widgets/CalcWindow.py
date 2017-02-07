# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 19:43:51 2014

@author: Ben
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 17:19:44 2013

@author: Ben
"""

import sys
import PyQt4.QtGui as QtGui
from PyQt4.QtCore import SIGNAL

from numpy import mod


class CalcWindow(QtGui.QWidget):
    """This class operates the graphism of the instrument connectic"""
    # All the ports that can be used
    AVAILABLE_PORTS = []
    # Number of instrument that can be connected
    num_channels = 0
    color_set = ['cyan', 'black', 'blue', 'red', 'green',
                 'orange', 'magenta', 'maroon', 'plum', 'violet']

    def __init__(self, availiable_ports=["GPIB0::" + str(i) for i in range(30)], parent=None):
        super(CalcWindow, self).__init__(parent)
        # This is a grid strictured layout
        self.grid = QtGui.QGridLayout()
        # initilize the lists
        self.set_lists(-1)
        self.resize(480, 600)

    def __del__(self):
        print("exited calculation window")

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
        self.tb_list = []
        self.color_btn_list = []
        # Empty text boxes called Line Edit where the user can write which ever
        # title for plotting purposes
        self.var_name_le_list = []
        # Contains the names of the instruments' driver's modules
        self.calculation_le_list = []

        # sets the headers for the buttons
        if self.num_channels > 0:
            self.headers = ["Color", "Name", "Calculation"]
            for i, hdr_text in enumerate(self.headers):
                header = QtGui.QLabel(hdr_text)
                self.grid.addWidget(header, 0, i)

            for i in range(self.num_channels):
                self.create_line()

            if first_init:

                # set the layout and add a spacer bar
                self.vertical_layout = QtGui.QVBoxLayout(self)
                self.vertical_layout.setObjectName("vertical_layout")
                self.vertical_layout.addLayout(self.grid)
                spacer_item = QtGui.QSpacerItem(
                    20, 183, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
                self.vertical_layout.addItem(spacer_item)
                self.setLayout(self.vertical_layout)
        else:
            if first_init:
                pass
            else:
                self.resetLayout()

    def create_line(self, msg="", color=None):
        #        print "line created "+msg
        self.create_color_btn(self.color_btn_list, 0, color)
        self.create_lineedit(self.var_name_le_list, 1, width=50)
        self.create_lineedit(self.calculation_le_list, 2)

    def remove_lastline(self):
        # decrease the number of channels by one
        self.num_channels = self.num_channels - 1
        # group the different lists into one list to save space
        box_array = [self.color_btn_list,
                     self.var_name_le_list, self.calculation_le_list]
        # remove one widget from the lists and the layout
        for box in box_array:
            widget = box[self.num_channels]
            box.remove(widget)
            self.grid.removeWidget(widget)
            try:
                widget.setParent(None)
            except:
                pass
            widget.close()

    def remove_all_lines(self):
        while self.num_channels > 0:
            self.remove_lastline()

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
        self.vertical_layout.addLayout(self.grid)
        spacer_item = QtGui.QSpacerItem(
            20, 183, QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vertical_layout.addItem(spacer_item)

    def create_color_btn(self, color_btn_list, col, color):
        index = len(color_btn_list)

        if not color:
            color = self.color_set[mod(index, 10)]

        btn = QtGui.QPushButton(self)
        btn.setObjectName("param_name_le_list " + str(index))
        btn.setStyleSheet('QPushButton {background-color: %s}' % color)
        btn.setFixedSize(20, 20)

        self.connect(btn, SIGNAL("clicked()"), self.color_btn_handler)
        # add the newly created widget to the list and tothe layout
        color_btn_list.append(btn)
        self.grid.addWidget(btn, index + 1, col, 1, 1)

    def create_lineedit(self, le_list, col, label_text="Name", width=None):
        index = len(le_list)
        le = QtGui.QLineEdit(self)
        le.setObjectName("param_name_le_list " + str(index))
        self.connect(le, SIGNAL("textEdited(QString)"), self.lineEdit_handler)
        # add the newly created widget to the list and tothe layout
        le_list.append(le)
        self.grid.addWidget(le, index + 1, col, 1, 1)

        if width:
            le.setFixedWidth(width)

    def lineEdit_handler(self, string):

        self.emit(SIGNAL("labelsChanged()"))
        pass
#        print string
        # find on which line the user edited the lineEdit
        # box_index=self.var_name_le_list.index(self.sender())
        # le=self.var_name_le_list[box_index]

        # label=str(le.text())
        # if the label is to be empty it will be replaced by the parameter name
        # if label=="":
        # here I would delete this line
        # pass

    def color_btn_handler(self):
        btn = self.sender()
        idx = self.color_btn_list.index(btn)

        color = QtGui.QColorDialog.getColor(initial=btn.palette().color(1))
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

    def get_label_list(self):
        calcs = self.get_calculation_list()
        if calcs[-1] == '':
            return []
        else:
            return [str(le.text()) for le in self.var_name_le_list]

    def get_calculation_list(self):
        return [str(le.text()) for le in self.calculation_le_list]

    def get_calculation_nb(self):
        calcs = self.get_calculation_list()
        if calcs[-1] == '':
            return 0
        else:
            return len (calcs)
       # return len(self.calculation_le_list)

    def get_color_list(self):
        calcs = self.get_calculation_list()
        if calcs[-1] == '':
            return []
        else:
            return [str(btn.palette().color(1).name()) for btn in self.color_btn_list]

    def load_settings(self, fname):
        """ Load in instrument and initial plot settings from a file"""
        try:
            settings_file = open(fname)

            self.remove_all_lines()

            for line in settings_file:
                self.num_channels = self.num_channels + 1

                # file format is comma-separated list of settings for each channel
                # but commas may also occur in the python line, so only split
                # on the first two
                settings = line.split(',', 2)
                instr_type = settings[0].strip()

                if instr_type.upper() == 'CALC':
                    self.create_line()
                    self.var_name_le_list[-1].setText(settings[1].strip())
                    self.calculation_le_list[-1].setText(settings[2].strip())
            settings_file.close()
            self.create_line()

        except:
            pass

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

    app = QtGui.QApplication(sys.argv)
    ex = CalcWindow()
    ex.show()

#    ex.remove_all_lines()
    sys.exit(app.exec_())
