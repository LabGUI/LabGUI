# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 04:17:45 2013

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
import sys

from collections import OrderedDict
from LabTools.Display import QtTools, PlotDisplayWindow
from types import MethodType

from LabTools.DataStructure import LabeledData
from LabTools.IO import IOTool

import numpy as np

import logging


class LoadPlotWidget(QWidget):

    def __init__(self, parent=None, load_fname=''):
        super(LoadPlotWidget, self).__init__(parent)

        # main layout of the form is the verticallayout
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.loadLayout = QHBoxLayout()

        self.verticalLayout.setObjectName("fileLayout")
        self.loadFileLabel = QLabel(self)
        self.loadFileLabel.setText("data file to load:")
        self.loadFileLineEdit = QLineEdit(self)
        self.loadFileLineEdit.setText(load_fname)
        self.loadFileButton = QPushButton(self)
        self.loadFileButton.setText("Browse")
        self.loadLayout.addWidget(self.loadFileLabel)
        self.loadLayout.addWidget(self.loadFileLineEdit)
        self.loadLayout.addWidget(self.loadFileButton)
        self.verticalLayout.addLayout(self.loadLayout)

        self.plotLayout = QHBoxLayout()
        self.plotLayout.setObjectName("plotLayout")
        self.plotButton = QPushButton(parent=self)
        self.plotButton.setText("Plot")

        self.plotLayout.addWidget(self.plotButton)
        #self.runLayout.addItem(QSpacerItem(20, 183,  QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.verticalLayout.addLayout(self.plotLayout)

#        spacerItem = QSpacerItem(20, 183, QSizePolicy.Minimum, QSizePolicy.Expanding)
#        self.verticalLayout.addItem(spacerItem)

        self.setLayout(self.verticalLayout)

        self.connect(self.loadFileButton, SIGNAL(
            'clicked()'), self.on_loadFileButton_clicked)
        self.connect(self.plotButton, SIGNAL(
            'clicked()'), self.on_plotButton_clicked)
        self.connect(self.loadFileLineEdit, SIGNAL(
            "textChanged(const QString &)"), self.text_changed)

    def on_loadFileButton_clicked(self):
        fname = str(QFileDialog.getOpenFileName(self, 'Load data from', './'))
        self.text_changed()
        if fname:
            self.loadFileLineEdit.setText(fname)

    def load_file_name(self):
        return self.loadFileLineEdit.text()

    def on_plotButton_clicked(self):
        self.plotButton.setDisabled(True)

    def text_changed(self):
        self.plotButton.setEnabled(True)


def create_plw_func(parent, load_fname = None):
    """
        add a new plot load window in the MDI area. The data and channels are loaded from a file
    """
    # maintain the previous functionality if file name not passed in
    if not load_fname:
        load_fname = str(parent.widgets["loadPlotWidget"].load_file_name())
        
    logging.info("loading %s for plot"%(load_fname))

    extension = load_fname.rsplit('.')[len(load_fname.rsplit('.')) - 1]
#        print extension

    if extension == "adat":
        [data, labels] = IOTool.load_file_windows(load_fname, '\t')
    elif extension == "adat2":
        [data, labels] = IOTool.load_file_windows(load_fname)
    elif extension == "a5dat":
        data, param = load_experiment(load_fname)
        data = np.transpose(np.array(data))
        labels = {}
        labels["param"] = ["Vc", "T", "P"]
    elif extension == "ldat":
        lb_data = LabeledData(fname = load_fname)
        data = lb_data.data
        labels = {}
        labels["param"] = lb_data.labels
    else:
        [data, labels] = IOTool.load_file_windows(load_fname)

#        [data,labels]=IOTool.load_file_windows(load_fname)

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
    logging.info("%i channels in total"% (nb_channels))
    plw = PlotDisplayWindow.PlotDisplayWindow(
        data_array=data, name="Past data file: " + load_fname, window_type="Past", default_channels=nb_channels, channel_controls=chan_contr)
    
    
    parent.connect(plw.mplwidget, SIGNAL(
        "limits_changed(int,PyQt_PyObject)"), parent.emit_axis_lim)
        
    parent.connect(parent.dataAnalyseWidget, SIGNAL(
        "data_set_updated(PyQt_PyObject)"), plw.update_plot)
        
    parent.connect(parent.dataAnalyseWidget, SIGNAL(
        "update_fit(PyQt_PyObject)"), plw.update_fit)
        
    parent.connect(parent, SIGNAL("remove_fit()"), plw.remove_fit)

    try:
        for i, param in enumerate(labels['param']):
            plw.lineEdit_Name[i].setText(param)
    except:
        pass
    
    try:
        plw.set_axis_ticks(IOTool.load_pset_file(load_fname, labels['param']))
    except:
        pass

#        self.dataAnalyseWidget.refresh_active_set()
    
    plw.update_labels(labels['param'])
    parent.dataAnalyseWidget.update_data_and_fit(data)
#        plw.update_plot(data)
    parent.zoneCentrale.addSubWindow(plw)
    plw.show()

def add_widget_into_main(parent):
    mywidget = LoadPlotWidget(parent = parent)
    loadPlotDockWidget = QDockWidget("Load previous data file", parent)
    loadPlotDockWidget.setObjectName("loadPlotDockWidget")
    loadPlotDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    loadPlotDockWidget.setWidget(mywidget)
    
    parent.widgets["loadPlotWidget"] = mywidget
    parent.addDockWidget(Qt.RightDockWidgetArea, loadPlotDockWidget)
    
    
    parent.create_plw = MethodType(create_plw_func, parent, parent.__class__)
    
    parent.connect(parent.widgets["loadPlotWidget"].plotButton,
                 SIGNAL("clicked()"), parent.create_plw)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = LoadPlotWidget()
    ex.show()
    sys.exit(app.exec_())
