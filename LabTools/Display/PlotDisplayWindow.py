# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 13:18:32 2012

Copyright (C) 10th april 2015 Benjamin Schmidt
              23rd october 2015 Pierre-François Duc (MultiplePlotDisplayWindow)
License: see LICENSE.txt file

TODO:
    - add toolbar for plot navigation
    - more descriptive output in print 
    - disable appropriate inputs when acquisition starts
    - end thread more gracefully    
    - move instrument objects to main thread / shared?
    - print the right axes as well as the left
"""

from __future__ import division
import time
import datetime

import numpy as np

from matplotlib import dates
from matplotlib import ticker

from collections import OrderedDict

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtCore import Qt, pyqtSignal, QRect, QRectF

else:

    import PyQt4.QtGui as QtGui
    from PyQt4.QtCore import Qt, QRect, QRectF
    from PyQt4.QtCore import SIGNAL

try:
    import QtTools
except:
    from . import QtTools


try:
    from mplZoomWidget import MatplotlibZoomWidget
except:
    from . import mplZoomWidget
    MatplotlibZoomWidget = mplZoomWidget.MatplotlibWidget
try:
    import ui_plotdisplaywindow
except:
    from . import ui_plotdisplaywindow
try:
    from PlotPreferences import marker_set, line_set, color_blind_friendly_colors
except:
    from .PlotPreferences import marker_set, line_set, color_blind_friendly_colors


# this label is used to know when the axis should be a formated time
# year, month, day, hours, mintues etc...
TIME_LABEL = "Time(s)"

import logging
logging.basicConfig(level=logging.DEBUG)


def isnparray(an_array):
    if not isinstance(an_array, np.ndarray):
        msg = "The argument passed as a numpy array is of type '%s'" % (
            type(an_array).__name__)
        return TypeError(msg)
    else:
        return True


VOID_NPARRAY = np.array([])

"""
This describe what element will be displayed on each line of 
the window option panel. It does it row by row, chan_contr contain 
each row element which consist of the label and the type of the objet.

The label can be any string, the type has to be predefined
"""
chan_contr = OrderedDict()
chan_contr["groupBox_Name"] = ["Channel", "lineEdit"]
chan_contr["groupBox_X"] = ["X", "radioButton"]
chan_contr["groupBox_Y"] = ["YL", "checkBox"]
chan_contr["groupBox_YR"] = ["YR", "checkBox"]
chan_contr["groupBox_fit"] = ["fit", "radioButton"]
chan_contr["groupBox_invert"] = ["+/-", "checkBox"]
chan_contr["groupBox_color"] = ["Col", "colorButton"]
chan_contr["groupBox_marker"] = ["M", "comboBox"]
chan_contr["groupBox_line"] = ["L", "comboBox"]

PLOT_WINDOW_TYPE_LIVE = "Live"
PLOT_WINDOW_TYPE_PAST = "Past"
PLOT_WINDOW_TITLE_PAST = "Past data file : "


def get_groupBox_purpouse(name):
    return name.split("_")[1]


class PlotDisplayWindow(QtGui.QMainWindow, ui_plotdisplaywindow.Ui_PlotDisplayWindow):
    """
    The argument 'channel_controls' should be an OrderedDict object (from collections import OrderedDict)\n
    Each key will be a unique identifier of the channel control, the item should consist of a list for which the first element is the label of the channel control and the second element, the type of QtQui.\n
    It need to be either 'lineEdit','radioButton','checkBox' or 'comboBox', any other keyword will create an error.\n
    What callback function is associated with each control can be defined in the method 'add_channel_control'

    """

    def __init__(self, parent=None, data_array=np.array([]),
                 name="Main Window", window_type=PLOT_WINDOW_TYPE_LIVE,
                 default_channels=10, channel_controls=chan_contr,
                 labels=[]):
        # run the initializer of the class inherited from
        super(PlotDisplayWindow, self).__init__()

        self.window_type = window_type

        # store the choice of channel controls parameters
        self.channel_controls = channel_controls

        self.color_set = color_blind_friendly_colors(default_channels)
        # this is where most of the GUI is made
        self.setupUi(self, self.channel_controls)
        self.customizeUi(default_channels)

        # Create an instance of auto-hiding widget which will contain the channel controls
        self.autoHide = QtTools.QAutoHideDockWidgets(
            Qt.RightDockWidgetArea, self)

        # axes and figure initialization - short names for convenience
        self.fig = self.mplwidget.figure
        self.setWindowTitle(name)

        self.ax = self.mplwidget.axes
        self.axR = self.mplwidget.axesR

        self.ax.xaxis.set_major_formatter(
            ticker.ScalarFormatter(useOffset=False))
        self.major_locator = self.ax.xaxis.get_major_locator()
        self.ax.yaxis.set_major_formatter(
            ticker.ScalarFormatter(useOffset=False))
        self.axR.yaxis.set_major_formatter(
            ticker.ScalarFormatter(useOffset=False))

        self.fig.canvas.draw()

        # this is for a feature that doesn't exist yet
        self.history_length = 0

        self.num_channels = 0
        self.left_lines = []
        self.right_lines = []

        self.legend_box = False
        self.data_legends = []

        if labels:
            self.update_labels(labels)

        else:
            # Fills self.lineEdit_Name = [], self.comboBox_Type = [], self.comboBox_Instr = []. self.comboBox_Param = []
            # Whenever connect(obbject,SIGNAL(),function) is used it will call the function whenever the object is manipulated or something emits the same SIGNAL()
            for i in range(default_channels):
                self.add_channel_controls()

        # objects to hold line data. Plot empty lists just to make handles
        # for line objects of the correct color

        # create data_array attribute and use channel 0 as X by default
        self.data_array = data_array
        self.chan_X = 0
        self.time_Xaxis = False


###### OPTION MENU SETUP ######

        self.optionMenu = self.menuBar().addMenu("Options")
        self.displayLegendsAction = QtTools.create_action(self, "Display/hide legends", slot=self.change_legend_box_state,
                                                          icon=None, tip="Display/hide legends on the figure")

        self.optionMenu.addAction(self.displayLegendsAction)

    def closeEvent(self, event):
        """
        when the window get close the destruction of the layout is handled
        properly by the second parent class method
        """
        logging.debug("Closing the Plotdisplaywindow")
        self.__delete_layouts__()

    def customizeUi(self, default_channels):

        # this will be a dictionnary with the same keys as self.channel_controls corresponding to list
        # of 'N_channel' control Qwidgets.
        self.channel_objects = {}
        for name, item in self.channel_controls.items():
            self.channel_objects[name] = []

        # create a layout within the blank "plot_holder" widget and put the
        # custom matplotlib zoom widget inside it. This way it expands to fill
        # the space, and we don't need to customize the ui_recordsweep.py file
        self.gridLayout_2 = QtGui.QGridLayout(self.plot_holder)

        if not USE_PYQT5:
            self.gridLayout_2.setMargin(0)

        self.gridLayout_2.setObjectName("gridLayout_2")

        self.mplwidget = MatplotlibZoomWidget(self.plot_holder)
        self.mplwidget.setObjectName("mplwidget")
        self.gridLayout_2.addWidget(self.mplwidget, 0, 0, 1, 1)

    def add_channel_controls(self):
        """
        create an instance of each of the channel control objects for a new channel, assign the settings and link to the callback function.\n
        It also create an empty line for each axis.
        """
        # index of boxes to create
        i = self.num_channels

        self.num_channels = self.num_channels + 1

        def pos_LE(x): return 20 * (x + 1)

        line1, = self.ax.plot([], [])
        line2, = self.axR.plot([], [])

        for name, item in self.channel_controls.items():
            # this value is set to true if there is one new QtGui object per line
            multiple_item = True

            if item[1] == "radioButton":

                self.channel_objects[name].append(QtGui.QRadioButton(
                    self.groupBoxes[name]))
                self.channel_objects[name][i].setText("")

                if name == "groupBox_X":

                    if USE_PYQT5:

                        self.channel_objects[name][i].toggled.connect(
                            self.XRadioButtonHandler)

                    else:

                        self.connect(self.channel_objects[name][i],
                                     SIGNAL("toggled(bool)"),
                                     self.XRadioButtonHandler)

            elif item[1] == "checkBox":

                self.channel_objects[name].append(
                    QtGui.QCheckBox(self.groupBoxes[name]))
                self.channel_objects[name][i].setText("")

                if USE_PYQT5:

                    self.channel_objects[name][i].stateChanged.connect(
                        self.YCheckBoxHandler)

                else:

                    self.connect(self.channel_objects[name][i],
                                 SIGNAL("stateChanged(int)"),
                                 self.YCheckBoxHandler)

            elif item[1] == "comboBox":

                self.channel_objects[name].append(
                    QtGui.QComboBox(self.groupBoxes[name]))

                if get_groupBox_purpouse(name) == "marker":

                    cbb_list = marker_set

                elif get_groupBox_purpouse(name) == "line":

                    cbb_list = line_set

                self.channel_objects[name][i].addItems(cbb_list)
#                self.channel_objects[name][i].setStyleSheet ("QComboBox::drop-down {border-width: 0px;} QComboBox::down-arrow {image: url(noimg); border-width: 0px;}")
                self.channel_objects[name][i].setMaxVisibleItems(len(cbb_list))

                if USE_PYQT5:

                    self.channel_objects[name][i].currentIndexChanged.connect(
                        self.ComboBoxHandler)

                else:

                    self.connect(self.channel_objects[name][i],
                                 SIGNAL("currentIndexChanged(int)"),
                                 self.ComboBoxHandler)

            elif item[1] == "lineEdit":

                self.channel_objects[name].append(
                    QtGui.QLineEdit(self.groupBoxes[name]))
                self.channel_objects[name][i].setText(
                    QtGui.QApplication.translate("RecordSweepWindow",
                                                 "",
                                                 None))
                if USE_PYQT5:

                    self.channel_objects[name][i].textEdited.connect(
                        self.lineEditHandler)

                else:

                    self.connect(self.channel_objects[name][i],
                                 SIGNAL("textEdited(QString)"),
                                 self.lineEditHandler)

            elif item[1] == "colorButton":

                self.channel_objects[name].append(
                    QtGui.QPushButton(self.groupBoxes[name]))
                if len(self.color_set) == 0:
                    color = []
                else:
                    color = self.color_set[np.mod(i, len(self.color_set))]

                line1.set_color(color)
                line2.set_color(color)

                self.channel_objects[name][i].setStyleSheet(
                    'QPushButton {background-color: %s}' % color)
                self.channel_objects[name][i].setFixedSize(15, 15)

                if USE_PYQT5:

                    self.channel_objects[name][i].clicked.connect(
                        self.colorButtonHandler)

                else:

                    self.connect(self.channel_objects[name][i],
                                 SIGNAL("clicked()"),
                                 self.colorButtonHandler)

            elif item[1] == "single_comboBox":

                if self.channel_objects[name] == []:
                    self.channel_objects[name] = QtGui.QComboBox(
                        self.groupBoxes[name])

                    if USE_PYQT5:

                        self.channel_objects[name].currentIndexChanged.connect(
                            self.singleComboBoxHandler)
                    else:

                        self.connect(self.channel_objects[name],
                                     SIGNAL("currentIndexChanged(int)"),
                                     self.singleComboBoxHandler)

                    self.channel_objects[name].setObjectName(name + item[1])

                multiple_item = False

            if multiple_item:

                self.channel_objects[name][i].setObjectName(
                    "%s#%i" % (name, i))
                self.channel_objects[name][i].setGeometry(QRect(7, 20*(i+1),
                                                                16, 16))

            else:

                self.channel_objects[name].setGeometry(QRect(7, 10*(i+1),
                                                             70, 16))

            # resize the comboBoxes and the lineEdit
            if item[1] == "lineEdit":

                self.channel_objects[name][i].setGeometry(QRect(10, pos_LE(i),
                                                                81, 16))

            elif item[1] == "comboBox":

                self.channel_objects[name][i].setGeometry(QRect(7, 20*(i+1),
                                                                32, 16))

            if multiple_item:

                self.channel_objects[name][i].show()

            else:

                self.channel_objects[name].show()
#        self.radio
        # create line objects and append them to self.ax[R].lines autoatically

    def list_channels_values(self):
        """list the current state of the window controls

            list the current state of the window controls in an array of string
        """
        lines = []

        for i in range(self.num_channels):

            line = ""

            for name, item in self.channel_controls.items():

                if item[1] == "radioButton":

                    line = "%s, %s" % (
                        line, int(self.channel_objects[name][i].isChecked()))

                elif item[1] == "checkBox":

                    line = "%s, %s" % (
                        line, int(self.channel_objects[name][i].isChecked()))

                elif item[1] == "comboBox":

                    line = "%s, '%s'" % (
                        line, self.channel_objects[name][i].currentText())

                elif item[1] == "lineEdit":

                    line = "%s, '%s'" % (
                        line, self.channel_objects[name][i].text())

                elif item[1] == "colorButton":

                    obj = self.channel_objects[name][i]
                    line = "%s, %s" % (line, obj.styleSheet()[-8:-1])

                elif item[1] == "single_comboBox":

                    line = "%s, %s" % (
                        line, self.channel_objects[name][i].currentText())

            lines.append(line)

        return lines

    def set_channels_values(self, lines):
        """set the states of the window controls

            set state of the window controls given an array of string
        """
#        print lines
        for i, line in enumerate(lines):

            if line:
                for j, name in enumerate(self.channel_controls):

                    #[name, role] of the channel control
                    item = self.channel_controls[name]

                    if item[1] == "radioButton" or item[1] == "checkBox":
                        # tick or untick the box, distinguish between 0 and
                        # any other number
                        try:

                            state = int(line[j])
                            self.channel_objects[name][i].setChecked(state)

                        except ValueError:

                            logging.warning(
                                "'%s' is not a boolean value" % line[j])

                    elif item[1] == "comboBox":
                        # sets the index of the object in the combobox
                        idx = self.channel_objects[name][i].findText(line[j])
                        self.channel_objects[name][i].setCurrentIndex(idx)

                    elif item[1] == "lineEdit":
                        # sets the text in the lineEdit
                        self.channel_objects[name][i].setText(line[j])

                    elif item[1] == "colorButton":

                        obj = self.channel_objects[name][i]
                        obj.setStyleSheet('QPushButton {background-color: %s}'
                                          % (line[j]))

                    elif item[1] == "single_comboBox":
                        # sets the index of the object in the combobox
                        idx = self.channel_objects[name][i].findText(line[j])
                        self.channel_objects[name][i].setCurrentIndex(idx)

    """#####################################################################"""
    """These handler function take action when someone interact with the button, checkbox, lineEdit etc... the names are explicit"""

    def change_legend_box_state(self):
        self.legend_box = not self.legend_box
        self.update_legends()

    def XRadioButtonHandler(self):
        #        print "X clicked"
        obj = self.sender()
        name = obj.objectName()
        name = str(name.split("#")[0])

        for num, box in enumerate(self.channel_objects[name]):
            if box.isChecked():

                self.chan_X = num
                label = self.channel_objects["groupBox_Name"][num].text()
                self.ax.set_xlabel(label)

                if label == TIME_LABEL:

                    self.time_Xaxis = True

                    hfmt = self.set_axis_time(want_format=True)

                    self.ax.xaxis.set_major_locator(self.major_locator)
                    self.ax.xaxis.set_major_formatter(hfmt)

                    major_ticks = self.ax.xaxis.get_major_ticks()
#

                    for i, tick in enumerate(major_ticks):
                        if i == 1:
                            n = tick.label.get_text()
                            label_i = n.split(" ")[0]

                        tick.label.set_rotation(45)

                else:

                    self.time_Xaxis = False
                    self.ax.xaxis.set_major_locator(self.major_locator)
                    self.ax.xaxis.set_major_formatter(
                        ticker.ScalarFormatter(useOffset=False))

                    for tick in self.ax.xaxis.get_major_ticks():
                        tick.label.set_rotation('horizontal')

        # Avoid updating the labels the first time the user click on the button
        if self.is_any_checkbox_checked("groupBox_Y") and\
           self.is_any_checkbox_checked("groupBox_YR"):
            self.update_plot()

    def YCheckBoxHandler(self):
        """Update which data is used for the Y axis (both left and right)"""
        tot_label = []
#        print "Y clicked"
        obj = self.sender()
        name = obj.objectName()
        name = str(name.split("#")[0])

        for num, box in enumerate(self.channel_objects[name]):
            if box.isChecked():
                label = str(self.channel_objects["groupBox_Name"][num].text())
                #unit = self.UNITS[str(self.comboBox_Param[num].currentText())]
                tot_label.append(label)  # + " (" + unit + ")" + ", "

        if get_groupBox_purpouse(name) == "Y":
            self.set_Y_axis_label(tot_label)
        elif get_groupBox_purpouse(name) == "YR":
            self.set_YR_axis_label(tot_label)

        self.update_plot()

    def ComboBoxHandler(self, num):
        """This fonction is triggered when someones toggle a combobox"""
        obj = self.sender()
        name = obj.objectName()

        name, idx = name.split("#")
        name = str(name)
        idx = int(idx)

        if get_groupBox_purpouse(name) == "marker":

            self.set_marker(idx, str(obj.currentText()))
            self.update_legends()

        elif get_groupBox_purpouse(name) == "line":

            self.set_linestyle(idx, str(obj.currentText()))
            self.update_legends()

    def singleComboBoxHandler(self, num):
        """
        this takes care of the signal sent by a single combo box (as opposed to one combobox per row)
        The single combo box should be used to plot X versus Y or YR for different data sets in a children class of this one
        """
        pass

    def colorButtonHandler(self):
        obj = self.sender()
        name = obj.objectName()

        name, idx = name.split("#")
        name = str(name)
        idx = int(idx)

        color = QtGui.QColorDialog.getColor(initial=obj.palette().color(1))
        obj.setStyleSheet('QPushButton {background-color: %s}' % color.name())
#        btn.palette().color(1).name()
        self.set_color(idx, str(color.name()))

    def lineEditHandler(self, mystr):
        obj = self.sender()
        name = obj.objectName()
        name, idx = name.split("#")
        name = str(name)
        idx = int(idx)

        if self.channel_objects["groupBox_X"][idx].isChecked():
            self.set_X_axis_label(self.channel_objects[name][idx].text())
            self.update_plot()

        self.update_legends()

    def set_axis_ticks(self, ticks):

        if not len(ticks) == 3:

            print("some ticks are missing, you should have ticks for X, YL and YR axes")

        else:

            for t in ticks[1]:
                self.channel_objects["groupBox_Y"][t].setCheckState(True)
#                print "Y",str(self.lineEdit_Name[t].text())
            for t in ticks[2]:
                self.channel_objects["groupBox_YR"][t].setCheckState(True)
#                print "YR",str(self.lineEdit_Name[t].text())

            self.channel_objects["groupBox_X"][ticks[0]].setChecked(True)
#            print "X",str(self.lineEdit_Name[ticks[0]].text())

    def get_X_axis_label(self):
        """Update which data is used for the X axis"""
        for num, box in enumerate(self.channel_objects["groupBox_X"]):
            if box.isChecked():
                label = str(self.channel_objects["groupBox_Name"][num].text())
        # getting rid of the eventual units
        if label.find('(') == -1:
            pass
        else:
            label = label[0:label.rfind('(')]
        return label

    def get_Y_axis_labels(self):
        """Update which data is used for the Y axis (both left and right)"""
        labels = []

        for num, box in enumerate(self.channel_objects["groupBox_Y"]):
            if box.isChecked():
                label = str(self.channel_objects["groupBox_Name"][num].text())
                label = label[0:label.rfind('(')]
                labels.append(label)
        for num, box in enumerate(self.channel_objects["groupBox_YR"]):
            if box.isChecked():
                label = str(self.channel_objects["groupBox_Name"][num].text())
                label = label[0:label.rfind('(')]
                if not label in labels:
                    labels.append(label)
        return labels

    def get_X_axis_index(self):
        """Update which data is used for the X axis"""
        index = 0
        for num, box in enumerate(self.channel_objects["groupBox_X"]):
            if box.isChecked():
                index = num
        return index

    def get_fit_axis_index(self):
        """Update which data is used for the fitting procedure"""
        index = 0
        for num, box in enumerate(self.channel_objects["groupBox_fit"]):
            if box.isChecked():
                index = num
        return index

    def get_Y_axis_index(self):
        """Update which data is used for the Y axis (only left)"""
        index = 0
        for num, box in enumerate(self.channel_objects["groupBox_Y"]):
            if box.isChecked():
                index = num
        return index

    def set_X_axis_label(self, newlabel):
        """Update which label is used for the X axis"""
        self.ax.set_xlabel(newlabel)

    def set_Y_axis_label(self, newlabel):
        """Update which label is used for the Y axis"""
        if np.size(newlabel) > 1:

            tot_label = newlabel[0]

            for i in range(1, np.size(newlabel)):

                tot_label = "%s, %s" % (tot_label, newlabel[i])

            newlabel = tot_label

        elif np.size(newlabel) == 1:

            if not isinstance(newlabel, str) and np.iterable(newlabel):
                # a list with only one element
                newlabel = newlabel[0]

        else:

            newlabel = ''

        self.ax.set_ylabel(newlabel)

    def set_YR_axis_label(self, newlabel):
        """Update which label is used for the YR axis"""
        if np.size(newlabel) > 1:

            tot_label = newlabel[0]

            for i in range(1, np.size(newlabel)):

                tot_label = "%s, %s" % (tot_label, newlabel[i])

            newlabel = tot_label

        elif np.size(newlabel) == 1:

            if not isinstance(newlabel, str) and np.iterable(newlabel):
                # a list with only one element
                newlabel = newlabel[0]

        else:

            newlabel = ''

        self.axR.set_ylabel(newlabel)

    def is_any_checkbox_checked(self, group_box_name):
        """loop through the checkbox of a list and look if at least one is on"""

        answer = False

        if group_box_name in self.channel_objects:

            for box in self.channel_objects[group_box_name]:

                if box.isChecked():

                    answer = True

        return answer

    def convert_timestamp(self, timestamp):

        try:

            dts = [datetime.datetime.fromtimestamp(ts) for ts in timestamp]

            dts = np.array(dts)

            return dates.date2num(dts)  # converted

        except:

            return timestamp

    def set_axis_time(self, want_format=False):
        """
            convert the time to a certain format
        """

        if want_format:

            hfmt = dates.DateFormatter('%m/%d %H:%M')

            if self.data_array.size > 0:

                time_interval = self.data_array[-1,
                                                self.chan_X]-self.data_array[0, self.chan_X]

                if time_interval < 500:
                    hfmt = dates.DateFormatter('%m/%d %H:%M:%S')

            return hfmt

        else:

            time_data = self.convert_timestamp(self.data_array[:, self.chan_X])

            return time_data

    def set_marker(self, idx, marker):
        """change the marker style of the plotted line in position idx"""
        if idx < len(self.ax.lines):
            self.ax.lines[idx].set_marker(marker)
            self.axR.lines[idx].set_marker(marker)
        self.mplwidget.rescale_and_draw()

    def set_linestyle(self, idx, linesty):
        """change the style of the plotted line in position idx"""
        if idx < len(self.ax.lines):
            self.ax.lines[idx].set_linestyle(linesty)
            self.axR.lines[idx].set_linestyle(linesty)
        self.mplwidget.rescale_and_draw()

    def set_color(self, idx, color):
        """change the color of the plotted line in position idx"""
        if idx < len(self.ax.lines):
            self.ax.lines[idx].set_color(color)
            self.axR.lines[idx].set_color(color)
        self.mplwidget.rescale_and_draw()

    def update_markers(self, marker_list):
        """change the marker style of all the lines according to a maker list"""
        for idx, m in enumerate(marker_list):
            if idx < len(self.ax.lines):
                self.ax.lines[idx].set_marker(m)
                self.axR.lines[idx].set_marker(m)
        self.mplwidget.rescale_and_draw()

    def update_colors(self, color_list):
        """change the color of all the lines according to a color list"""
        for idx, color in enumerate(color_list):
            if idx < len(self.ax.lines):
                self.ax.lines[idx].set_color(color)
                self.axR.lines[idx].set_color(color)
        self.mplwidget.rescale_and_draw()

    def update_labels(self, label_list):
        """change the label of all the lines according to a label list"""

        for idx, label_text in enumerate(label_list):
            if idx == len(self.channel_objects["groupBox_Name"]):
                self.add_channel_controls()

            self.channel_objects["groupBox_Name"][idx].setText(label_text)

    def update_legends(self): # check the zip, as range is no longer a list
        """update the property of the lines in the legend box"""
        if self.legend_box:
            handles = []
            legends = []
            for i, handle, legend, in zip(range(self.num_channels), self.ax.lines, self.data_legends['L']):
                if legend == "no data":
                    pass
                else:
                    legends.append(legend)
                    handles.append(handle)
            for i, handle, legend, in zip(range(self.num_channels), self.axR.lines, self.data_legends['R']):
                if legend == "no data":
                    pass
                else:
                    legends.append(legend)
                    handles.append(handle)
            self.ax.legend(handles, legends, numpoints=1, frameon=False)
        else:
            self.ax.legend([], [], frameon=False)

        self.mplwidget.rescale_and_draw()

    def update_plot(self, data_array=None):
        """
            take a matrix (data_array) with a number of rows equal to the number of channel/lines in the window and plot them along the line direction
            it only plots if the checkbox of the line is checked
        """

        if isnparray(data_array) == True:
            logging.debug("update the data_array")
            self.data_array = data_array

        if self.data_array.size > 0:
            # if the number of columns is more than the number of control boxes
            try:
                num_channels = self.data_array.shape[1]
            except:
                num_channels = np.size(self.data_array, 1)

            # if there is more instruments than channel numbers we expand the channels on the window
            while self.num_channels < num_channels:
                self.add_channel_controls()

            # there is a different treatment if x is choosen to be a time axis or quantity measured by an instrument
            if self.time_Xaxis:
                xdata = self.set_axis_time()
            else:
                xdata = self.data_array[:, self.chan_X]

            self.data_legends = {'L': [], 'R': []}
            # go through the channels and update the lines for those who are checked
            for chan_Y, [line_L, line_R] in enumerate(zip(self.ax.lines, self.axR.lines)):

                if self.data_array.size > 0:

                    if self.channel_objects["groupBox_invert"][chan_Y].isChecked():
                        ydata = -self.data_array[:, chan_Y]
                    else:
                        ydata = self.data_array[:, chan_Y]

                    # look which checkbox is checked and plot corresponding data
                    if self.channel_objects["groupBox_Y"][chan_Y].isChecked() and self.data_array.size > 0:
                        line_L.set_data(xdata, ydata)
                        self.data_legends['L'].append(
                            str(self.channel_objects["groupBox_Name"][chan_Y].text()))
                    else:
                        line_L.set_data([], [])
                        self.data_legends['L'].append("no data")

                    # look which checkbox is checked and plot corresponding data
                    if self.channel_objects["groupBox_YR"][chan_Y].isChecked() and self.data_array.size > 0:
                        line_R.set_data(xdata, ydata)
                        self.data_legends['R'].append(
                            str(self.channel_objects["groupBox_Name"][chan_Y].text()))
                    else:
                        line_R.set_data([], [])
                        self.data_legends['R'].append("no data")
        else:
            # if an empty array was given we set the lines to empty arrays
            for line_L, line_R in zip(self.ax.lines, self.axR.lines):
                line_L.set_data([], [])
                line_R.set_data([], [])

        self.mplwidget.rescale_and_draw()

        self.update_legends()

        # rescale the ticks so that we can always read them
        try:

            self.fig.tight_layout()

        except ValueError as e:

            if "left cannot be >= right" in str(e):
                pass
                # it seems to be a platform dependent error
            elif "ordinal must be >= 1" in str(e):
                try:

                    initial_array = [time.time()]

                    for i in range(self.num_channels - 1):

                        initial_array.append(np.nan)

                    self.update_plot(np.array([initial_array]))
                except:
                    pass
                    # whenever the time format is on and the data array is empty
            else:
                raise e

        except RuntimeError:
            pass
            # whenever the time format is on and the data array is empty
            # this is an ugly fix but at least the error doesn,t show anymore

    def update_fit(self, fitp):
        """
            take a matrix (data_array) with a number of lines equal to 2 and a number of rows equal the number of lines in self.data_array
            and plot line 1 as a function of line 2
            right now there is only the possibility to create one fit at the time as we wanted to be able to access the line number and modify the fit or delete it. 
            we can always plot more things on the plot area but we wanted to have some control on the objects
        """

        logging.debug(fitp)

        # if the number of columns is more than the number of control boxes
        if self.num_channels == len(self.ax.lines):
            line, = self.ax.plot([], [], "-", color="#e62e00", linewidth=2)
            line, = self.ax.plot([], [], "--", color="#e62e00", linewidth=2)

        # if there is a resctiction on the data set
        idx_start = int(fitp["limits"][0])
        idx_stop = int(fitp["limits"][1])
        # there is a different treatment if x is choosen to be a time axis or quantity measured by an instrument
        if self.time_Xaxis:
            xdataw = self.set_axis_time()
        else:
            xdataw = self.data_array[:, self.chan_X]

        xdata = xdataw[idx_start:idx_stop]

        fitYw = fitp["fit_func"](xdataw, *fitp["fitp_val"])
        fitY = fitp["fit_func"](xdata, *fitp["fitp_val"])

        self.ax.lines[-1].set_data(xdataw, fitYw)

        self.ax.lines[-2].set_data(xdata, fitY)

        # call a method defined in the module mplZoomwidget.py
        self.mplwidget.rescale_and_draw()

        # rescale the ticks so that we can always read them
        try:
            self.fig.tight_layout()
        except ValueError as e:
            if "left cannot be >= right" in e:
                pass
                # it seems to be a platform dependent error
            else:
                raise e

    def remove_fit(self):
        """
            remove the last line on the ax as this position is by default reserved for the fit function. There is probaly a cleverer way to do so...
        """
        if self.num_channels < len(self.ax.lines):
            self.ax.lines[-1].set_data([], [])
            self.ax.lines[-2].set_data([], [])

    def print_figure(self, file_name="unknown"):
        """Sends the current plot to a printer"""

        printer = QtGui.QPrinter()

        # Get the printer information from a QPrinter dialog box
        dlg = QtGui.QPrintDialog(printer)
        if(dlg.exec_() != QtGui.QDialog.Accepted):
            return

        p = QtGui.QPainter(printer)

        # dpi*3 because otherwise it looks pixelated (not sure why, bug?)
        dpi = printer.resolution()

#        # copy the current figure contents to a standard size figure
#        fig2 = plt.figure(figsize=(8,5), dpi = dpi)
#
#        ax = fig2.add_subplot(1,1,1)
#        for line in self.ax.lines:
#            if line.get_xdata() != []:
#                ax.plot (line.get_xdata(), line.get_ydata(), label= line.get_label())
#        ax.set_xlim(self.ax.get_xlim())
#        ax.set_ylim(self.ax.get_ylim())
#        ax.set_xlabel(self.ax.get_xlabel())
#        ax.set_ylabel(self.ax.get_ylabel())
#
#        self.fig.savefig(
#        # support for printing right axes should go here
#
#        # Shink current axis by 20%
#        box = ax.get_position()
#        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        #ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        # goal: print the figure with the same aspect ratio as it's shown on the
        # screen, but fixed width to fill the page nicely

        margin_inches = 0.5
        paper_width = 8.5

        max_width = paper_width - 2*margin_inches
        max_height = 7

        width = self.fig.bbox_inches.width
        height = self.fig.bbox_inches.height

        ratio = height/width
        if ratio > max_height/max_width:
            # scale on width, because otherwise won't fit on page.
            dpi_scale = max_height/height
            height = max_height
            width = ratio/height
        else:
            dpi_scale = max_width/width
            width = max_width
            height = ratio * width

        self.fig.savefig("temp.png", dpi=dpi * dpi_scale * 10)

        # half inch margins
        margin_top = 0.5*dpi
        margin_left = 0.5*dpi

        # matplotlib's svg rendering has a bug if the data extends beyond the
        # plot limits. Below is what would be used for temp.svg
        #svg = QtSvg.QSvgRenderer("temp.svg")
        #svg.render(p, QRectF(margin_top,margin_left, 8*dpi, 5*dpi))

        p.drawImage(QRectF(margin_top, margin_left, width*dpi, height*dpi),
                    QtGui.QImage("temp.png", format='png'))
        p.drawText(margin_left, 600, "Data recorded to: " + file_name)
        p.end()

    def is_plot_display_window(self):
        """used to differentiate PlotDisplayWindow from LoadPlotWindow"""
        return True


"""
This describe what element will be displayed on each line of the window option panel.
It does it row by row, chan_contr contain each row element which consist of the label and the type of the objet.
The label can be any string, the type has to be predifined
"""
chan_contr = OrderedDict()
chan_contr["groupBox_Name"] = ["Channel", "lineEdit"]
chan_contr["groupBox_X"] = ["Set", "checkBox"]
chan_contr["groupBox_Y"] = ["Z", "checkBox"]
chan_contr["groupBox_YR"] = ["phi", "checkBox"]
chan_contr["groupBox_fit"] = ["fit", "checkBox"]
#chan_contr["groupBox_invert"]= ["+/-","checkBox"]
chan_contr["groupBox_color"] = ["Col", "colorButton"]
chan_contr["groupBox_marker"] = ["M", "comboBox"]
chan_contr["groupBox_line"] = ["L", "comboBox"]


class MultiplePlotDisplayWindow(PlotDisplayWindow):
    """
    The argument 'channel_controls' should be an OrderedDict object (from collections import OrderedDict)\n
    Each key will be a unique identifier of the channel control, the item should consist of a list for which the first element is the label of the channel control and the second element, the type of QtQui.\n
    It need to be either 'lineEdit','radioButton','checkBox' or 'comboBox', any other keyword will create an error.\n
    What callback function is associated with each control can be defined in the method 'add_channel_control'
    The data sets should be in LabeledData instances
    """

    def __init__(self, parent=None, data_array=np.array([]), name="Main Window", default_channels=10, channel_controls=chan_contr):
        # run the initializer of the class inherited from
        super(MultiplePlotDisplayWindow, self).__init__(parent=parent, data_array=data_array,
                                                        name=name, default_channels=default_channels, channel_controls=channel_controls)

        self.sets_to_plot = []
        self.add_channel_controls()
        self.num_channels = self.num_channels-1

    """#####################################################################"""
    """These handler function take action when someone interact with the button, checkbox, lineEdit etc... the names are explicit"""

    def YCheckBoxHandler(self):
        """Update which data is used for the Y axis (both left and right) and chooses to activate or not a set"""
        obj = self.sender()
        name = obj.objectName()

        name, sender_ID = name.split("#")
        name = str(name)
        # number of the checkbox in the list (from 0 to self.num_channels)
        sender_ID = int(sender_ID)

        # If the last box is being played with, then it means that we want to either select all of them or deselect all of them
        if sender_ID == self.num_channels:
            # This is the current state of this button
            check_all = self.channel_objects[name][self.num_channels].isChecked(
            )

            # then somebody just clicked on that button and we need to change
            for box in self.channel_objects[name]:
                box.setChecked(check_all)

        if get_groupBox_purpouse(name) == "X":
            #            for i in selected_boxes:
            state_X = self.channel_objects["groupBox_X"][sender_ID].isChecked()
            self.channel_objects["groupBox_Y"][sender_ID].setChecked(state_X)
            self.channel_objects["groupBox_YR"][sender_ID].setChecked(state_X)

        elif get_groupBox_purpouse(name) == "Y":
            # remembers the state of the YR
            state_Y = self.channel_objects["groupBox_Y"][sender_ID].isChecked()
            state_YR = self.channel_objects["groupBox_YR"][sender_ID].isChecked(
            )

            state_X = state_Y or state_YR

            self.channel_objects["groupBox_X"][sender_ID].setChecked(state_X)

            # restores the state of the YR
            self.channel_objects["groupBox_YR"][sender_ID].setChecked(state_YR)

        elif get_groupBox_purpouse(name) == "YR":
            state_Y = []
            # remembers the state of the Y
            state_Y = self.channel_objects["groupBox_Y"][sender_ID].isChecked()
            state_YR = self.channel_objects["groupBox_YR"][sender_ID].isChecked(
            )

            state_X = state_Y or state_YR

            self.channel_objects["groupBox_X"][sender_ID].setChecked(state_X)

            # restores the state of the Y
            self.channel_objects["groupBox_Y"][sender_ID].setChecked(state_Y)
#            for box,state in zip(self.channel_objects["groupBox_Y"],state_Y):
#                box.setChecked(state)

        self.update_plot()

    def update_labels(self, label_list):
        """change the label of all the lines according to a label list"""

        super(MultiplePlotDisplayWindow, self).update_labels(label_list)
        self.channel_objects["groupBox_Name"][self.num_channels].setText(
            "Select all")

    def update_plot(self, data_array=VOID_NPARRAY):
        """
            take a LabeledData vector of LabeledData (data_array with labels) with a number of elements equal to the number of channel/lines in the window and plot the matrix (where the X and YR and YL are predifined)
            it only plots if the checkbox of the line is checked
        """

        if not isnparray(data_array) == True:
            raise isnparray(data_array)

        if not data_array == VOID_NPARRAY:
            self.data_array = data_array

        if self.data_array.ncols > 0:
            # if the number of columns is more than the number of control boxes
            try:
                num_channels = self.data_array.ncols
            except:
                num_channels = self.data_array.size

            # if there is more instruments than channel numbers we expand the channels on the window
            while self.num_channels < num_channels:
                print("MultiplePlotDisplayWindow.update_plot : adding more channel")
                self.add_channel_controls()

            # go through the channels and update the lines for those who are checked
            for data, chan_Y, line_L, line_R in zip(self.data_array.columns(), np.arange(self.num_channels), self.ax.lines, self.axR.lines):

                if self.data_array.ncols > 0:

                    # If the Set checkbox is unticked the data will not be displayed
                    if self.channel_objects["groupBox_X"][chan_Y].isChecked():

                        # look which checkbox is checked and plot corresponding data
                        if self.channel_objects["groupBox_Y"][chan_Y].isChecked() and self.data_array.ncols > 0:
                            line_L.set_data(data[:, 0], data[:, 1])
                        else:
                            line_L.set_data([], [])

                        # look which checkbox is checked and plot corresponding data
                        if self.channel_objects["groupBox_YR"][chan_Y].isChecked() and self.data_array.ncols > 0:
                            line_R.set_data(data[:, 0], data[:, 2])
                        else:
                            line_R.set_data([], [])
                    else:
                        # if one unticked the Set checkbox, it should disable the set and therefore the plot
                        line_L.set_data([], [])
                        line_R.set_data([], [])
        else:
            # if an empty array was given we set the lines to empty arrays
            for line_L, line_R in zip(self.ax.lines, self.axR.lines):
                line_L.set_data([], [])
                line_R.set_data([], [])
        self.mplwidget.rescale_and_draw()


"""
This describe what element will be displayed on each line of the window option panel.
It does it row by row, chan_contr contain each row element which consist of the label and the type of the objet.
The label can be any string, the type has to be predifined.
If you choose the type single_comboBox there will be only one combobox for all the rows
"""
chan_contr = OrderedDict()
chan_contr["groupBox_Name"] = ["Channel", "lineEdit"]
chan_contr["groupBox_setnum"] = ["Set", "checkBox"]
chan_contr["groupBox_X"] = ["X", "single_comboBox"]
chan_contr["groupBox_Y"] = ["Y", "single_comboBox"]
# chan_contr["groupBox_YR"]=["YR","single_comboBox"]
chan_contr["groupBox_fit"] = ["fit", "checkBox"]
#chan_contr["groupBox_invert"]= ["+/-","checkBox"]
chan_contr["groupBox_color"] = ["Col", "colorButton"]
chan_contr["groupBox_marker"] = ["M", "comboBox"]
chan_contr["groupBox_line"] = ["L", "comboBox"]


class SetsPlotDisplayWindow(PlotDisplayWindow):
    """
    The argument 'channel_controls' should be an OrderedDict object (from collections import OrderedDict)\n
    Each key will be a unique identifier of the channel control, the item should consist of a list for which the first element is the label of the channel control and the second element, the type of QtQui.\n
    It need to be either 'lineEdit','radioButton','checkBox', 'comboBox' or single_comboBox any other keyword will create an error.\n
    What callback function is associated with each control can be defined in the method 'add_channel_control'
    The data sets should be in LabeledData instances
    """

    def __init__(self, parent=None, data_sets_array=VOID_NPARRAY, name="Main Window", default_channels=10, channel_controls=chan_contr):

        num_channels = np.size(data_sets_array)
        if num_channels == 0:
            num_channels = default_channels

        # run the initializer of the class inherited from
        super(SetsPlotDisplayWindow, self).__init__(parent=parent, name=name,
                                                    default_channels=num_channels, channel_controls=channel_controls)

        # these names shall correspond to the column name of the LabeledData instances one wants to plot
        self.X_axis_name = ""
        self.Y_axis_name = ""
        self.YR_axis_name = ""

        self.legend_box = False
        self.data_legends = []

        self.update_data_sets(data_sets_array)

###### OPTION MENU SETUP ######

        self.optionMenu = self.menuBar().addMenu("Options")
        self.displayLegendsAction = QtTools.create_action(self, "Display/hide legends", slot=self.change_legend_box_state,
                                                          icon=None, tip="Display/hide legends on the figure")

        self.optionMenu.addAction(self.displayLegendsAction)

    """#####################################################################"""
    """These handler function take action when someone interact with the button, checkbox, lineEdit etc... the names are explicit"""

    def singleComboBoxHandler(self, num):
        obj = self.sender()
        name = obj.objectName()

        item_name = str(obj.currentText())

        if "groupBox_X" in name:
            self.X_axis_name = item_name
            self.set_X_axis_label(item_name)
        elif "groupBox_Y" in name:
            self.Y_axis_name = item_name
            self.set_Y_axis_label(item_name)
        elif "groupBox_YR" in name:
            self.YR_axis_name = item_name
            self.set_YR_axis_label(item_name)

        self.update_plot()

    def change_legend_box_state(self):
        self.legend_box = not self.legend_box
#        print self.legend_box
        self.update_legends()

    def change_single_comboBox_items(self, groupbox_id, newItems):
        """change the list of items of the comboBox that has the given groupbox_id"""

        if groupbox_id in self.channel_objects.keys():
            # clear the comboBox
            self.channel_objects[groupbox_id].clear()
            # add the new items
            self.channel_objects[groupbox_id].addItems(newItems)
            self.channel_objects[groupbox_id].setMaxVisibleItems(len(newItems))
        else:
            logging.warning(
                "The groupbox_id '%s' is unknown, please use one groupbox_id among this list" % (groupbox_id))
            logging.warning(self.channel_objects.keys())

    def update_labels(self, label_list):
        """change the label of all the lines according to a label list"""

        super(SetsPlotDisplayWindow, self).update_labels(label_list)

    def update_data_sets(self, data_sets_array=[]):
        """this function expects an array of"""

        data_sets_array = np.array(data_sets_array)

        if not np.size(data_sets_array) == 0:
            self.data_sets_array = data_sets_array

            labels = self.data_sets_array[0].labels
            test_labels_consistency = np.arange(len(self.data_sets_array))

            for i, data_set in enumerate(self.data_sets_array):
                # tests that all the labels of each data sets are the same
                test_labels_consistency[i] = (labels == data_set.labels)

            if test_labels_consistency.all() == True:
                logging.debug(
                    "All the labels of LabeledData instances are the same")
                for gb_id in ["groupBox_X", "groupBox_Y"]:
                    self.change_single_comboBox_items(gb_id, labels)
                self.change_single_comboBox_items("groupBox_Y", labels)
                for i, le in enumerate(self.channel_objects["groupBox_Name"]):
                    le.setText(self.data_sets_array[i].dataset_name)
            else:
                logging.warning(
                    "Some labels of LabeledData instances are not the same")
        else:
            logging.warning(
                "The data sets array is empty, so it wasn't updated")

    def update_legends(self):
        if self.legend_box:
            handles = []
            legends = []
            for i, handle, legend, in zip(range(self.num_channels), self.ax.lines, self.data_legends):
                if legend == "no data":
                    pass
                else:
                    legends.append(legend)
                    handles.append(handle)
            self.ax.legend(handles, legends)
        else:
            self.ax.legend([], [])

        self.mplwidget.rescale_and_draw()

    def update_plot(self, data_sets_array=[]):
        """
            take a LabeledData vector of LabeledData (data_array with labels) with a number of elements equal to the number of channel/lines in the window and plot the matrix (where the X and YR and YL are predifined)
            it only plots if the checkbox of the line is checked
        """

        data_sets_array = np.array(data_sets_array)

        if not np.size(data_sets_array) == 0:
            self.data_sets_array = data_sets_array

        self.data_legends = []
        # go through the channels and update the lines for those who are checked
        for data, chan_set, line_L, line_R in zip(self.data_sets_array, np.arange(self.num_channels), self.ax.lines, self.axR.lines):

                # If the Set checkbox is unticked the data will not be displayed
            if self.channel_objects["groupBox_setnum"][chan_set].isChecked():
                line_L.set_data(data[self.X_axis_name], data[self.Y_axis_name])
                self.data_legends.append(
                    str(self.channel_objects["groupBox_Name"][chan_set].text()))
            else:
                self.data_legends.append("no data")
                line_L.set_data([], [])
#

        self.update_legends()


import sys


def test_pdw():
    app = QtGui.QApplication(sys.argv)
    form = PlotDisplayWindow()

    form.show()
    app.exec_()


def test_update_plot():
    app = QtGui.QApplication(sys.argv)
    form = PlotDisplayWindow()
    form.update_plot(2)
#    form.show()
    app.exec_()


def test_timestamp():

    EPOCH_DATE = datetime.datetime(1969, 12, 31, 20, 0, 0)

    now = datetime.datetime.now()
    import random

    # create a data array
    t = []
    d = []
    for i in np.arange(20, 0, -1):
        if i == 10:
            d.append(np.nan)
        else:
            d.append(random.random())
        t.append((now - datetime.timedelta(seconds=i) -
                  EPOCH_DATE).total_seconds())

    data = np.transpose(np.vstack([t, d]))

    app = QtGui.QApplication(sys.argv)
    form = PlotDisplayWindow(labels=[TIME_LABEL, 'data(arb)'])
    form.update_plot(data)
    form.show()
    app.exec_()


def test_pdw_save_setting():
    app = QtGui.QApplication(sys.argv)
    form = PlotDisplayWindow()
    form.list_channels_values()
    form.show()
    app.exec_()


def test_pdw_load_setting():
    app = QtGui.QApplication(sys.argv)
    form = PlotDisplayWindow()

    lines = []
    lines.append(['Time(s)', '1', '-2', '0', '0', '0', '#117733', 's', '-'])
    lines.append(['dt(s)', '0', 'er', '0', '0', '0', '#88CCEE', 'None', '-'])
    lines.append(['PRESSURE(psi)', '0', '0', '0',
                  '0', '0', '#332288', 'None', '-'])
    lines.append(['dt(s)', '0', '0', '1', '0', '0', '#FFFF', 'o', '-'])
    lines.append(['2(Torr)', '0', '0', '1', '0', '0', '#CC6677', 'None', '-'])

    form.set_channels_values(lines)
    form.show()
    app.exec_()



# This snippet makes it run as a standalone program
if __name__ == "__main__":
    #    test_pdw_save_setting()
    test_pdw_load_setting()
#    test_timestamp()


#    app = QtGui.QApplication(sys.argv)
#    from GuiTools.DataStructure import LabeledData
#    data=LabeledData(np.array([[1,2,3],[4,5,6],[7,8,9]]),["a","b","c"],dataset_name="Num1")
#    data2=LabeledData(np.array([[10,11,12],[13,14,15],[16,17,18]]),["a","b","c"],dataset_name="autre")
#
#    form = SetsPlotDisplayWindow(data_sets_array=[data,data2])
##    data=np.array([np.arange(10) for a in range(10)])
# data=np.loadtxt("sample_name_TEST_1130_001.dat")
#
##    from GuiTools.DataStructure import LabeledData
# data=LabeledData(np.array([[1,2,3],[4,5,6],[7,8,9]]),["a","b","c"],dataset_name="Num1")
# data2=LabeledData(np.array([[10,11,12],[13,14,15],[16,17,18]]),["a","b","c"],dataset_name="autre")
# form.update_data_sets([data,data2])
#    form.show()
#    app.exec_()

#    data=np.loadtxt("sample_name_TEST_1128_008.dat")
#    time_interval=data[-1,0]-data[0,0]
#    print time_interval
#    time_data = convert_timestamp(data[:,0])
##        xlim = convert_timestamp(self.ax.get_xlim())
##        print xlim
##    print time_data
#        # matplotlib date format object
#    hfmt = dates.DateFormatter('%m/%d %H:%M:%S')
#
#    fig=plt.figure()
#    ax=fig.add_subplot(111)
#    ax.plot(time_data,data[:,1])
#    plt.xticks(rotation='vertical')
# plt.xticks()
# plt.subplots_adjust(bottom=.3)
#        #plt.show()
# for li in self.ax.lines:
# if li.get_xdata().size >0:
####                print li.get_data()
# li.set_xdata(time_data)
##
# ax.xaxis.set_major_locator()
#    ax.xaxis.set_major_formatter(hfmt)
#
##    print ax.xaxis.get_xticklabels()
#
#    for i in ax.xaxis.get_major_ticks():
#        print i.label.get_text()
##
###        print "ready to draw"
# self.mplwidget.rescale_and_draw()
#
#
#
#    plt.show()
