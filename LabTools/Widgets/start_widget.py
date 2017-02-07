# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:58:03 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

import sys
import re

from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL

from LabTools.IO import IOTool



class StartWidget(QWidget):

    def __init__(self, parent=None):
        super(StartWidget, self).__init__(parent)

        # main layout of the form is the verticallayout

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        #moved the script stuff to a separate widget that lives in the toolbar

        self.outputLayout = QHBoxLayout()
        self.outputLayout.setObjectName("outputLayout")
        self.outputFileLabel = QLabel(self)
        self.outputFileLabel.setText("Output File:")
        self.outputFileLineEdit = QLineEdit(self)
        self.outputFileButton = QPushButton(self)
        self.outputFileButton.setText("Browse")
        self.outputLayout.addWidget(self.outputFileLabel)
        self.outputLayout.addWidget(self.outputFileLineEdit)
        self.outputLayout.addWidget(self.outputFileButton)
        self.verticalLayout.addLayout(self.outputLayout)

        self.headerTextEdit = QPlainTextEdit("")
        fontsize = self.headerTextEdit.fontMetrics()
        self.headerTextEdit.setFixedHeight(fontsize.lineSpacing() * 8)
        self.verticalLayout.addWidget(self.headerTextEdit)
        
        # moved the start stop button to the toolbar only

        self.setLayout(self.verticalLayout)

        self.outputFileLineEdit.setText(IOTool.get_file_name())

        self.connect(self.outputFileButton, SIGNAL(
            'clicked()'), self.on_outputFileButton_clicked)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum))
        
    def on_outputFileButton_clicked(self):
        fname = str(QFileDialog.getSaveFileName(self, 'Save output file as',
                                                self.outputFileLineEdit.text()))
        if fname:
            self.outputFileLineEdit.setText(fname)

    def increment_filename(self):
        # search for the regular expression that corresponds to the incrementable
        # file name
        p = re.compile(r"_[0-9]{3}[.]dat$")
        fname = str(self.outputFileLineEdit.text())
        found = p.findall(fname)
        print(("found:" + str(found)))
        if not found == []:
            ending = found[0]
            num = int(ending[1:4]) + 1
            fname = fname.replace(ending, "_%3.3d.dat" % num)
            self.outputFileLineEdit.setText(fname)

    def get_header_text(self):
        text = str(self.headerTextEdit.toPlainText())
        if text:
            text = "# " + text.replace("\n", "\n#") + "\n"
            return text
        else:
            return ""

if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = StartWidget()
    ex.show()
    sys.exit(app.exec_())
