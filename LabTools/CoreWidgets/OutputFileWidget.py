# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:58:03 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

from LabTools.IO import IOTool
import sys
import re
import logging


from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtCore import pyqtSignal, Qt

else:

    import PyQt4.QtGui as QtGui
    from PyQt4.QtCore import SIGNAL, Qt


# from os import path UNCOMMENT TO HAVE ABS PATH


class OutputFileWidget(QtGui.QWidget):

    def __init__(self, parent=None, fname=IOTool.get_file_name()):
        super(OutputFileWidget, self).__init__(parent)

        self.parent = parent
        # main layout of the form is the verticallayout

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # moved the script stuff to a separate widget that lives in the toolbar

        self.outputLayout = QtGui.QHBoxLayout()
        self.outputLayout.setObjectName("outputLayout")
        self.outputFileLabel = QtGui.QLabel(self)
        self.outputFileLabel.setText("Output File:")
        self.outputFileLineEdit = QtGui.QLineEdit(self)
        self.outputFileButton = QtGui.QPushButton(self)
        self.outputFileButton.setText("Browse")
        self.outputLayout.addWidget(self.outputFileLabel)
        self.outputLayout.addWidget(self.outputFileLineEdit)
        self.outputLayout.addWidget(self.outputFileButton)
        self.verticalLayout.addLayout(self.outputLayout)

        self.headerTextEdit = QtGui.QPlainTextEdit("")
        fontsize = self.headerTextEdit.fontMetrics()
        self.headerTextEdit.setFixedHeight(fontsize.lineSpacing() * 8)
        self.verticalLayout.addWidget(self.headerTextEdit)

        # moved the start stop button to the toolbar only

        self.setLayout(self.verticalLayout)

        self.outputFileLineEdit.setText(fname)

        self.outputFileButton.clicked.connect(self.on_outputFileButton_clicked)

        self.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum))

    def on_outputFileButton_clicked(self):

        fname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save output file as',
                                                      self.outputFileLineEdit.text()))

        if fname:

            self.outputFileLineEdit.setText(fname)

    def increment_filename(self):
        # search for the regular expression that corresponds to the incrementable
        # file name
        p = re.compile(r"_[0-9]{3}[.]dat$")
        fname = self.get_output_fname()

        found = p.findall(fname)
#        print(("found:" + str(found)))
        if not found == []:
            ending = found[0]
            num = int(ending[1:4]) + 1
            fname = fname.replace(ending, "_%3.3d.dat" % num)
            self.outputFileLineEdit.setText(fname)

    def get_header_text(self):

        text = str(self.headerTextEdit.toPlainText())
        data_str = ""
        if self.parent is not None:
            if hasattr(self.parent, "get_user_data"):
                data = self.parent.get_user_data()
                #data_str = ""
                for name, value in data.items():
                    data_str += "D'%s', '%s'\n" % (name, value)
        if text:
            # need space to prevent possible error
            text = "# " + text.replace("\n", "\n#") + "\n"

            if data_str != "":
                text += "#" + data_str.strip("\n").replace("\n", "\n#") + "\n"

            return text

        else:
            if data_str != "":
                return "#" + data_str.strip("\n").replace("\n", "\n#") + "\n"
            else:
                return ""

    def set_header_text(self, text):
        self.headerTextEdit.setPlainText(text.rstrip('\n'))

    def get_output_fname(self):

        return str(self.outputFileLineEdit.text())


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    ofname = IOTool.get_file_name(config_file_path=parent.config_file)
    mywidget = OutputFileWidget(parent=parent, fname=ofname)
    #mywidget = OutputFileWidget(parent=parent, fname=path.abspath(ofname))

    outDockWidget = QtGui.QDockWidget("Output file and header text", parent)
    outDockWidget.setObjectName("OutputFileDockWidget")
    outDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['OutputFileWidget'] = mywidget

    outDockWidget.setWidget(mywidget)
    parent.addDockWidget(Qt.RightDockWidgetArea, outDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(outDockWidget.toggleViewAction())


if __name__ == "__main__":
    #ofname = IOTool.get_file_name(config_file_path="C:\\Users\\admin\\Documents\\LabGUI\\config.txt")
    #print("ofname", ofname)
    app = QtGui.QApplication(sys.argv)
    ex = OutputFileWidget()
    ex.show()
    sys.exit(app.exec_())
