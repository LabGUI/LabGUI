# -*- coding: utf-8 -*-
"""
Created on Tue Nov 05 04:17:45 2013

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
import sys


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

if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = LoadPlotWidget()
    ex.show()
    sys.exit(app.exec_())
