# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:58:03 2013

@author: Benjamin Schmidt, zackorenberg
"""

import sys

from LocalVars import USE_PYQT5

if USE_PYQT5:

    from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                                 QFileDialog, QHBoxLayout, QApplication, QComboBox, QSizePolicy)

else:

    from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QHBoxLayout, QApplication, QComboBox, QSizePolicy)

try:
    from pathlib import Path
    PATHLIB=True
except:
    PATHLIB=False

import logging
from LabTools.IO import IOTool
import os

class ScriptWidget(QWidget):
    """widget with a dropdown and a browse button"""

    def __init__(self, parent=None, legacy = False):
        super(ScriptWidget, self).__init__(parent)

        self.LEGACY = legacy

        self.scriptLayout = QHBoxLayout()

        self.scriptFileLabel = QLabel(self)
        self.scriptFileLabel.setText("Script to run:")

        if self.LEGACY is True:
            self.scriptFileLineEdit = QLineEdit(self)
        else:
            self.scriptFileComboBox = self.create_combobox()

        self.scriptFileButton = QPushButton(self)
        self.scriptFileButton.setText("Browse")

        self.scriptLayout.addWidget(self.scriptFileLabel,0)

        if self.LEGACY is True:
            self.scriptLayout.addWidget(self.scriptFileLineEdit,1)
        else:
            self.scriptLayout.addWidget(self.scriptFileComboBox,1)

        self.scriptLayout.addWidget(self.scriptFileButton,0)

        self.setLayout(self.scriptLayout)

        self.fname = IOTool.get_script_name()
        self.set_script(self.fname)

        self.scriptFileButton.clicked.connect(self.on_scriptFileButton_clicked)

    def on_scriptFileButton_clicked(self):

        if USE_PYQT5:

            fname, fmt = QFileDialog.getOpenFileName(
                self, 'Load script from', './scripts/',
                'Script files (*.py)')
        else:

            fname = str(QFileDialog.getOpenFileName(
                self, 'Load script from', './scripts/',
                'Script files (*.py)'))

        if fname:
            if self.LEGACY is True:
                self.scriptFileLineEdit.setText(fname)
            else:
                self.set_script(fname)

    def get_script_fname(self):
        if self.LEGACY is True:
            return str(self.scriptFileLineEdit.text())
        else:
            return str(self.scriptFileComboBox.currentText())

    def create_combobox(self):
        cbb = QComboBox(self)
        cbb.setObjectName("comboBox")
        cbb.setStyleSheet(
            "QComboBox::drop-down {border-width: 0px;} \
QComboBox::down-arrow {image: url(noimg); border-width: 0px;}")
        # this allow the user to edit the content of the combobox input
        cbb.setEditable(True)

        cbb.setSizePolicy(QSizePolicy(
            QSizePolicy.Ignored, # instead of Expanding to allow shrinkage
            QSizePolicy.Fixed,
            QSizePolicy.ComboBox
        ))

        cbb.setMinimumWidth(55) # make it act similar to lineedit
        cbb.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)

        return cbb

    def fill_combobox(self):
        directory = os.path.dirname(self.fname)
        #files = os.listdir(directory)

        self.scriptFileComboBox.clear()
        self.scriptFileComboBox.addItems(
            [os.path.join(d, f) for d,_,files in os.walk(directory) for f in files if f[-3:].lower() == ".py"]
        )
        self.scriptFileComboBox.setCurrentText(self.fname)

    def set_script(self, script_name):
        if PATHLIB:
            self.fname = str(Path(script_name))
        else:
            self.fname = script_name

        if self.LEGACY is True:
            self.scriptFileLineEdit.setText(self.fname)
        else:
            self.fill_combobox()

    def load_settings(self, fname):
        """ Loads last script if saved to device settings"""

        try:
            settings_file = open(fname, 'r')
            settings_file_ok = True
        except IOError:

            settings_file_ok = False

        if not settings_file_ok:

            return []

        else:
            for setting_line in settings_file:

                # file format is comma-separated list of settings for each channel
                setting_line = setting_line.strip()
                if setting_line[0] != "#": continue

                line = setting_line[1:].strip().split(",")
                if line[0] == "script":
                    self.set_script(line[1])
                    return True
        return False


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    parent.widgets['ScriptWidget'] = ScriptWidget(parent)

    fname = IOTool.get_script_name(config_file_path=parent.config_file)

    parent.widgets['ScriptWidget'].set_script(fname)

    parent.instToolbar.addWidget(parent.widgets['ScriptWidget'])


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = ScriptWidget(legacy=True)
    directory = os.path.dirname(ex.fname)
    print(directory)
    for a, b, c in os.walk(directory):
        print(a,b,c)
    ex.show()
    ex2 = ScriptWidget(legacy=False)
    ex2.show()
    sys.exit(app.exec_())
