# -*- coding: utf-8 -*-
"""
Created on Jun 27

@author: zackorenberg

Meant to control which UserWidgets are configured to run
"""
"""
Created for GervaisLabs
"""

import sys

from types import MethodType
import logging
try:
    from LocalVars import USE_PYQT5
except:
    USE_PYQT5=True # default
import os

try:
    from LabTools.IO import IOTool
except:
    from .IO import IOTool

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon

else:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore


class UserWidgetManager(QtGui.QWidget):

    def __init__(self, parent=None, **kwargs):
        super(UserWidgetManager, self).__init__(**kwargs)

        self.parent = parent
        self.title = "User Widget Manager"
        if "LabTools" in os.getcwd():
            # we are in LabTools
            widget_path = os.path.dirname(__file__)

            self.icon = os.path.abspath("../images/icon_normal_py3.png")
        else:
            #cur_path = os.path.dirname(__file__)

            # find the path to the widgets folders
            #widget_path = os.path.join(cur_path, "LabTools")
            widget_path = os.path.dirname(__file__)


            self.icon = os.path.abspath("images/icon_normal_py3.png")

        self.setWindowIcon(QIcon(self.icon))
        self.setWindowTitle(self.title)
        # these are widgets which were added by users
        self.user_widget_path = os.path.join(widget_path, "UserWidgets")

        # this is the legitimate list of user widgets
        self.refresh_widgets_list()


        # Now create actual widget


        # listview stuff for widgets
        self.listview = QtGui.QListView(self)
        self.model = QStandardItemModel()
        self.listview.setModel(self.model)


        #config file selector

        self.configfileLayout = QtGui.QHBoxLayout()
        self.configfileLayout.setObjectName("configLayout")
        self.configFileLabel = QtGui.QLabel(self)
        self.configFileLabel.setText("Config File:")
        self.configFileLineEdit = QtGui.QLineEdit(self)
        self.configFileButton = QtGui.QPushButton(self)
        self.configFileButton.setText("Browse")
        self.configfileLayout.addWidget(self.configFileLabel)
        self.configfileLayout.addWidget(self.configFileLineEdit)
        self.configfileLayout.addWidget(self.configFileButton)

        self.configFilePath = IOTool.CONFIG_FILE_PATH
        self.configFileLineEdit.setText(self.configFilePath)

        self.configFileButton.clicked.connect(self.on_configFileButton_clicked)

        # footer buttons
        self.saveButton = QtGui.QPushButton('Save')
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.selectButton = QtGui.QPushButton('Select All')
        self.unselectButton = QtGui.QPushButton('Unselect All')

        # footer buttons event handling
        self.saveButton.clicked.connect(self.save_userwidget_selection_event)
        self.refreshButton.clicked.connect(self.refresh_all)
        self.selectButton.clicked.connect(self.select_all)
        self.unselectButton.clicked.connect(self.unselect_all)

        self.footerLayout = QtGui.QHBoxLayout()
        self.footerLayout.setObjectName("footerLayout")
        self.footerLayout.addWidget(self.saveButton)
        self.footerLayout.addWidget(self.refreshButton)
        self.footerLayout.addWidget(self.selectButton)
        self.footerLayout.addWidget(self.unselectButton)





        # Apply everything

        self.refresh_listview()

        # set the layout
        self.layout = QtGui.QVBoxLayout(self)
        # FORM LAYOUT self.layout = QtGui.QFormLayout(self)

        # add widgets to layout
        self.layout.addLayout(self.configfileLayout)
        self.layout.addWidget(self.listview)
        self.layout.addLayout(self.footerLayout)


        self.setLayout(self.layout)


    def get_config_userwidget_setting(self):
        return IOTool.get_user_widgets(config_file_path=self.configFilePath)

    def set_config_file_name(self, fname):
        self.configFilePath = fname
        self.configFileLineEdit.setText(self.configFilePath)
        self.refresh_all()

    def save_userwidget_selection(self):
        selected_widgets = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected_widgets.append(item.data())
        IOTool.set_user_widgets(selected_widgets)

    def refresh_all(self): # also an event
        self.refresh_widgets_list()
        self.refresh_listview()

    def refresh_listview(self):
        active_widgets = self.get_config_userwidget_setting()
        self.model.clear()
        for widget in self.widgets_list:
            item = QStandardItem(widget)
            item.setData(widget)
            item.setCheckable(True)
            item.setEditable(False)
            check = (QtCore.Qt.Checked \
                         if widget in active_widgets \
                         else QtCore.Qt.Unchecked
                     ) # for no partials!
            item.setCheckState(check)
            self.model.appendRow(item)
        self.listview.selectionModel().currentChanged.disconnect()
        self.listview.selectionModel()
        self.listview.selectionModel().currentChanged.connect(self.change_active_widgets)

    def refresh_widgets_list(self):
        self.widgets_list = [
            o.rstrip(".py")
            for o in os.listdir(self.user_widget_path)
            if o.endswith(".py") and "__init__" not in o
        ]

    def set_parent(self, new_parent):
        self.parent = new_parent

    ### EVENT STUFF ###
    def change_active_widgets(self, *args, **kwargs):
        pass
        #print("Active widget changed")
        #print(*args)
        #print(kwargs)
    def on_configFileButton_clicked(self):

        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Config file',
                                                      self.configFileLineEdit.text())[0])

        if fname:

            self.set_config_file_name(fname)
    def select_all(self):
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(QtCore.Qt.Checked)
    def unselect_all(self):
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(QtCore.Qt.Unchecked)

    def save_userwidget_selection_event(self):
        self.save_userwidget_selection()
        if self.parent is None:
            dia = QtGui.QMessageBox(self)
            dia.setWindowTitle("Save confirmation")
            dia.setText("Saved! Restart LabGUI to see changes.")
            dia.show()
        else:
            self.parent.relaunch(force=True)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)


    widget = UserWidgetManager()
    print(widget.widgets_list)
    widget.show()

    sys.exit(app.exec_())