# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:58:03 2013

Copyright (C) 10th april 2015 Benjamin Schmidt
License: see LICENSE.txt file
"""

import sys

from LocalVars import USE_PYQT5

if  USE_PYQT5:
    
    from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                                 QFileDialog, QHBoxLayout, QApplication)
    
else:
    
    from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QPushButton, 
                                 QFileDialog, QHBoxLayout, QApplication)


from LabTools.IO import IOTool


class ScriptWidget(QWidget):
    """widget with a lineEdit and a browse button"""

    def __init__(self, parent = None):
        super(ScriptWidget, self).__init__(parent)

        self.scriptLayout = QHBoxLayout()

        self.scriptFileLabel = QLabel(self)
        self.scriptFileLabel.setText("Script to run:")
        
        self.scriptFileLineEdit = QLineEdit(self)
        
        self.scriptFileButton = QPushButton(self)
        self.scriptFileButton.setText("Browse")
        
        self.scriptLayout.addWidget(self.scriptFileLabel)
        self.scriptLayout.addWidget(self.scriptFileLineEdit)
        self.scriptLayout.addWidget(self.scriptFileButton)

        self.setLayout(self.scriptLayout)

        self.scriptFileLineEdit.setText(IOTool.get_script_name())

        self.scriptFileButton.clicked.connect(self.on_scriptFileButton_clicked)

    def on_outputFileButton_clicked(self):
        
        fname = str(QFileDialog.getSaveFileName(self, 'Save output file as',
                                                self.outputFileLineEdit.text()))
                                                
        if fname:
            
            self.outputFileLineEdit.setText(fname)

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
            
            self.scriptFileLineEdit.setText(fname)

    def get_script_fname(self):
        
        return str(self.scriptFileLineEdit.text())


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain
    
    create a QDock widget and store a reference to the widget
    """    

    parent.widgets['ScriptWidget'] = ScriptWidget(parent)
    
    fname = IOTool.get_script_name(config_file_path = parent.config_file)    
    
    parent.widgets['ScriptWidget'].scriptFileLineEdit.setText(fname)
    
    parent.instToolbar.addWidget(parent.widgets['ScriptWidget'])



if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = ScriptWidget()
    ex.show()
    sys.exit(app.exec_())
