# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 04:17:45 2013

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""

#from PyQt4.QtGui import *
#from PyQt4.QtCore import Qt
#
import logging
import numpy as np
from LabTools.IO import IOTool
from LabTools.DataStructure import LabeledData
from types import MethodType
from LabTools.Display import PlotDisplayWindow
from collections import OrderedDict
import sys
import os


from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui

    from PyQt5.QtCore import Qt

else:

    import PyQt4.QtGui as QtGui

    from PyQt4.QtCore import Qt, SIGNAL


# to replace the data in OutputWidget
SET_OUTPUT_TEXT = False


class LoadPlotWidget(QtGui.QWidget):
    """this widget is used to replot previously measured data"""

    def __init__(self, parent=None, load_fname=''):

        super(LoadPlotWidget, self).__init__(parent)

        # main layout of the form is the verticallayout
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # first line contains a text zone and a browse button to
        # write the path to the data file to load
        self.loadLayout = QtGui.QHBoxLayout()
        self.loadLayout.setObjectName("fileLayout")

        # label for the user
        self.loadFileLabel = QtGui.QLabel(self)
        self.loadFileLabel.setText("data file to load:")

        # text zone
        self.loadFileLineEdit = QtGui.QLineEdit(self)
        self.loadFileLineEdit.setText(load_fname)

        # browse button
        self.loadFileButton = QtGui.QPushButton(self)
        self.loadFileButton.setText("Browse")

        # add the 3 widgets to the horizontal layout
        self.loadLayout.addWidget(self.loadFileLabel)
        self.loadLayout.addWidget(self.loadFileLineEdit)
        self.loadLayout.addWidget(self.loadFileButton)

        # add the horizontal layout to the vertical one
        self.verticalLayout.addLayout(self.loadLayout)

        # second line is a button to load and plot the data
        self.plotLayout = QtGui.QHBoxLayout()
        self.plotLayout.setObjectName("plotLayout")

        # plot button
        self.plotButton = QtGui.QPushButton(self)
        self.plotButton.setText("Plot")

        # add the widget to the layout
        self.plotLayout.addWidget(self.plotButton)

        # add the horizontal layout to the vertical one
        self.verticalLayout.addLayout(self.plotLayout)

        # third line is the name of the file (without the path)
        self.fileInfoLayout = QtGui.QHBoxLayout()
        self.fileInfoLayout.setObjectName("fileInfoLayout")

        # label
        self.loadFileLabelLabel = QtGui.QLabel(self)
        self.loadFileLabelLabel.setText("File :")

        # filename
        self.loadFileNameLabel = QtGui.QLabel(self)
        self.loadFileNameLabel.setText("")

        # add the widget to the layout
        self.fileInfoLayout.addWidget(self.loadFileLabelLabel)
        self.fileInfoLayout.addWidget(self.loadFileNameLabel)

        # add the horizontal layout to the vertical one
        self.verticalLayout.addLayout(self.fileInfoLayout)

        # fourth line is a large text zone to load the header of the file
        self.hdrtextLayout = QtGui.QHBoxLayout()
        self.hdrtextLayout.setObjectName("hdrtextLayout")

        # large text zone
        self.headerTextEdit = QtGui.QPlainTextEdit("")
        fontsize = self.headerTextEdit.fontMetrics()
        self.headerTextEdit.setFixedHeight(fontsize.lineSpacing() * 8)

        # add the widget to the layout
        self.hdrtextLayout.addWidget(self.headerTextEdit)

        # add the horizontal layout to the vertical one
        self.verticalLayout.addLayout(self.hdrtextLayout)

        # apply the vertical layout to the widget
        self.setLayout(self.verticalLayout)

        self.loadFileButton.clicked.connect(self.on_loadFileButton_clicked)

        self.plotButton.clicked.connect(self.on_plotButton_clicked)

        self.loadFileLineEdit.textChanged.connect(self.fname_changed)

    def on_loadFileButton_clicked(self):
        """open a file browser to select data file to be loaded"""

        # allow the user to set the path from the last file's path
        default_path = os.path.dirname(self.load_file_name())

        if default_path == '':

            default_path = './'

        if USE_PYQT5:

            fname, fmt = QtGui.QFileDialog.getOpenFileName(self,
                                                           'Load data from',
                                                           default_path)

            fname = str(fname)

        else:

            fname = str(QtGui.QFileDialog.getOpenFileName(self,
                                                          'Load data from',
                                                          default_path))

        # activate the plot button
        self.fname_changed()

        if fname:

            self.load_file_name(fname)

    def load_file_name(self, new_fname=None):
        """returns the whole file name indicated in the text zone

        or assign it if an argument is provided        
        """

        if new_fname == None:

            return str(self.loadFileLineEdit.text())

        else:
            # update the whole path and file name in the text zone
            self.loadFileLineEdit.setText(new_fname)

            # only select the file name for the label above the large text zone
            self.loadFileNameLabel.setText(os.path.basename(new_fname))

    def on_plotButton_clicked(self):
        """callback fonciton of the plot button"""
        self.plotButton.setDisabled(True)

    def fname_changed(self):
        """reactivate the plot button when the text in the text zone changes"""
        self.plotButton.setEnabled(True)

    def header_text(self, new_text=None):
        """get/set method for the text in the console"""

        if new_text == None:

            return str((self.headerTextEdit.toPlainText())).rstrip()

        else:

            self.headerTextEdit.setPlainText(new_text)


def create_plw(parent, load_fname=None):
    """
        add a new plot load window in the MDI area. The data and channels 
        are loaded from a file
    """
    # maintain the previous functionality if file name not passed in
    if not load_fname:
        load_fname = str(parent.widgets["loadPlotWidget"].load_file_name())

    logging.info("loading %s for plot" % (load_fname))

    extension = load_fname.rsplit('.')[len(load_fname.rsplit('.')) - 1]
#        print extension

    if extension == "ldat":
        lb_data = LabeledData(fname=load_fname)
        data = lb_data.data
        labels = {}
        labels["param"] = lb_data.labels
    else:
        try:
            data, labels = IOTool.load_file_windows(load_fname)
        except IndexError:  # empty file
            print(load_fname + " is empty")
            return
        except:
            print("Windows only currently supported. <create_plw>", sys.exc_info()[0])
            return
        if np.size(data) == 0:
            print("No data to read")
            return
        # add the header to the header text area
        if 'hdr' in labels.keys():
            parent.widgets["loadPlotWidget"].header_text(labels['hdr'])
        else:
            print("No headers present:", labels)

        if 'data' in labels.keys():
            parent.widgets['userDataWidget'].set_user_data_parse(labels['data'])

        # update the name information in the widget
        parent.widgets["loadPlotWidget"].load_file_name(load_fname)

        # store the hdr is there is more than one file
        parent.loaded_data_header[load_fname] = labels['hdr']
        if SET_OUTPUT_TEXT:
            parent.widgets['OutputFileWidget'].set_header_text(labels['hdr'])

    chan_contr = OrderedDict()
    chan_contr["groupBox_Name"] = ["Channel", "lineEdit"]
    chan_contr["groupBox_X"] = ["X", "radioButton"]
    chan_contr["groupBox_Y"] = ["YL", "checkBox"]
    chan_contr["groupBox_YR"] = ["YR", "checkBox"]
    chan_contr["groupBox_fit"] = ["fit", "radioButton"]
    chan_contr["groupBox_invert"] = ["+/-", "checkBox"]
    chan_contr["groupBox_marker"] = ["M", "comboBox"]
    chan_contr["groupBox_line"] = ["L", "comboBox"]

    logging.info("channel names are ", labels)
#        print data
    nb_channels = np.size(data, 1)
    logging.info("%i channels in total" % (nb_channels))
    plw = PlotDisplayWindow.PlotDisplayWindow(
        data_array=data,
        name=PlotDisplayWindow.PLOT_WINDOW_TITLE_PAST + load_fname,
        window_type=PlotDisplayWindow.PLOT_WINDOW_TYPE_PAST,
        default_channels=nb_channels,
        channel_controls=chan_contr)

    if USE_PYQT5:

        plw.mplwidget.limits_changed.connect(parent.emit_axis_lim)

        parent.widgets['AnalyseDataWidget'].update_fit.connect(
            plw.update_fit)

        parent.signal_remove_fit.connect(plw.remove_fit)

    else:

        parent.connect(plw.mplwidget, SIGNAL(
            "limits_changed(int,PyQt_PyObject)"), parent.emit_axis_lim)

        parent.connect(parent.widgets['AnalyseDataWidget'], SIGNAL(
            "update_fit(PyQt_PyObject)"), plw.update_fit)

        parent.connect(parent, SIGNAL("remove_fit()"), plw.remove_fit)

    try:
        for i, param in enumerate(labels['channel_labels']):
            plw.lineEdit_Name[i].setText(param)
    except:
        pass

    try:
        plw.set_axis_ticks(IOTool.load_pset_file(load_fname, labels['param']))
    except:
        pass

#        self.dataAnalyseWidget.refresh_active_set()

    plw.update_labels(labels['channel_labels'])
    parent.widgets['AnalyseDataWidget'].update_data_and_fit(data)
#        plw.update_plot(data)
    parent.zoneCentrale.addSubWindow(plw)
    plw.show()


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = LoadPlotWidget(parent=parent)

    # create a QDockWidget
    loadPlotDockWidget = QtGui.QDockWidget("Load previous data file", parent)
    loadPlotDockWidget.setObjectName("loadPlotDockWidget")
    loadPlotDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    loadPlotDockWidget.setWidget(mywidget)
    parent.addDockWidget(Qt.RightDockWidgetArea, loadPlotDockWidget)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets["loadPlotWidget"] = mywidget

    # Enable the toggle view action
    parent.windowMenu.addAction(loadPlotDockWidget.toggleViewAction())

    loadPlotDockWidget.hide()

    # assign a method to the LabGuiMain class to be run to create a
    # plot window with previous data
    # depending on the python version this fonction take different arguments
    if sys.version_info[0] > 2:

        parent.create_plw = MethodType(create_plw, parent)

    else:

        parent.create_plw = MethodType(create_plw, parent, parent.__class__)

    # create this dictionnary to remember the header text associated to
    # each loaded file
    parent.__class__.loaded_data_header = {}

    # connects the plot button clicked signal with the method to create a
    # plot window with previous data

    if USE_PYQT5:

        parent.widgets["loadPlotWidget"].plotButton.clicked.connect(
            parent.create_plw)

    else:

        parent.connect(parent.widgets["loadPlotWidget"].plotButton,
                       SIGNAL("clicked()"), parent.create_plw)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = LoadPlotWidget()
    ex.show()
    sys.exit(app.exec_())
