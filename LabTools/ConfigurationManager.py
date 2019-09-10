# -*- coding: utf-8 -*-
"""
Created on Jun 27

@author: zackorenberg

GUI for configuration, based on IOTools info
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
    from IO import IOTool

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon, QFontMetrics

else:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore

try:
    from LabTools import UserWidgetManager
except:
    from . import UserWidgetManager

LAYOUT = 'form' # other option is hbox

#### TYPE WIDGETS ####
class SelectorWidget(QtGui.QWidget):
    """
         Selector widget, data MUST have type!

         must have getValue and setValue and save and changeConfigFile attributes!
         """

    def __init__(self, name, data, config_file, parent=None, **kwargs):
        super(type(self), self).__init__(parent=parent, **kwargs)

        self.name = name
        self.data = data

        self.label = data['name']
        self.type = data['type']
        self.get = data['get']
        self.set = data['set']

        self.configFile = config_file
        # defaults
        self.options = data['options']
        self.current = self.get(config_file_path=self.configFile)
        # label

        self.op_label = QtGui.QLabel(self)
        self.op_label.setText(self.label)

        # dropdown stuff for widgets

        self.dropdown = QtGui.QComboBox()
        self.dropdown.addItems(self.options)
        self.dropdown.setCurrentText(self.current)
        self.dropdown.setObjectName(name)
        self.dropdown.activated[str].connect(self.change_setting)



        # set layout

        #self.layout = QtGui.QHBoxLayout(self)
        if LAYOUT == 'form':
            self.layout = QtGui.QFormLayout(self)
            self.layout.addWidget(self.op_label)
            self.layout.addWidget(self.dropdown)
        else:
            self.layout = QtGui.QHBoxLayout(self)
            self.layout.addWidget(self.op_label)
            self.layout.addWidget(self.dropdown)
        self.setLayout(self.layout)

    def change_setting(self):
        self.current = self.dropdown.currentText()

    #### REQUIRED FUNCTIONS ####
    def changeConfigFile(self, file):
        self.configFile = file
        self.reset()

    def setValue(self, value):
        if value in self.options:
            self.dropdown.setCurrentText(value)
        else:
            logging.warning("No data saved, as %s is not in options."%value)

    def save(self):
        self.set(self.getValue(), config_file_path=self.configFile)
        return self.getValue()

    def reset(self):
        self.setValue(self.get(config_file_path=self.configFile))

        return self.getValue()

    def getValue(self):
        return self.current
class ListViewWidget(QtGui.QWidget):
    """
        ListView widget, data MUST have type!

        must have getValue and setValue and save and changeConfigFile attributes!
        """

    def __init__(self, name, data, config_file, parent=None, **kwargs):
        super(type(self), self).__init__(parent=parent, **kwargs)

        self.name = name
        self.data = data

        self.label = data['name']
        self.type = data['type']
        self.get = data['get']
        self.set = data['set']

        self.configFile = config_file

        # label

        self.op_label = QtGui.QLabel(self)
        self.op_label.setText(self.label)

        # listview stuff for widgets
        self.listview = QtGui.QListView(self)
        self.model = QStandardItemModel()
        self.listview.setModel(self.model)

        self.options = data['options']
        self.current = self.get(config_file_path=self.configFile)
        self.refresh_listview()

        # set layout


        if LAYOUT == 'form':
            self.layout = QtGui.QFormLayout(self)
            self.layout.addWidget(self.op_label)
            self.layout.addWidget(self.listview)
        else:
            self.layout = QtGui.QHBoxLayout(self)
            self.layout.addWidget(self.op_label)
            self.layout.addWidget(self.listview)
        self.setLayout(self.layout)


    def refresh_all(self):
        self.reset()
    def refresh_listview(self):
        self.model.clear()
        for option in self.options:
            item = QStandardItem(option)
            item.setData(option)
            item.setCheckable(True)
            item.setEditable(False)
            check = (QtCore.Qt.Checked \
                         if option in self.current \
                         else QtCore.Qt.Unchecked
                     )  # for no partials!
            item.setCheckState(check)
            self.model.appendRow(item)

    #### REQUIRED FUNCTIONS ####
    def changeConfigFile(self, file):
        self.configFile = file
        self.reset()

    def setValue(self, value):
        if type(value) != list:
            value = list(value)
        self.current = value

        self.refresh_listview()

    def save(self):
        self.set(self.getValue(), config_file_path=self.configFile)
        return self.current

    def reset(self):
        if 'reset' in self.data:
            self.options = self.data['reset']()

        self.setValue(self.get(config_file_path=self.configFile))

        return self.getValue()

    def getValue(self):
        selected_widgets = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected_widgets.append(item.data())
        self.current = selected_widgets
        return selected_widgets
class FileWidget(QtGui.QWidget):
    """
    File selector widget, data MUST have type!

    must have getValue and setValue and save and changeConfigFile attributes!
    """
    def __init__(self, name,  data, config_file, parent=None, **kwargs):
        super(type(self), self).__init__(parent=parent, **kwargs)
        self.name = name
        self.data = data

        self.label = data['name']
        self.type = data['type']
        self.get = data['get']
        self.set = data['set']

        self.configFile = config_file

        # config file selector
        if LAYOUT == 'form':
            self.fileLayout = QtGui.QFormLayout()
        else:
            self.fileLayout = QtGui.QHBoxLayout()
        self.fileLayout.setObjectName("%sLayout" % name)
        self.FileLabel = QtGui.QLabel(self)
        self.FileLabel.setText(self.label)
        self.FileLineEdit = QtGui.QLineEdit(self)
        self.FileButton = QtGui.QPushButton(self)
        self.FileButton.setText("Browse")

        if LAYOUT == 'form':
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(self.FileLineEdit)
            hbox.addWidget(self.FileButton)
            self.fileLayout.addRow(self.FileLabel, hbox)
        else:
            self.fileLayout.addWidget(self.FileLabel)
            self.fileLayout.addWidget(self.FileLineEdit)
            self.fileLayout.addWidget(self.FileButton)

        self.FilePath = self.get(config_file_path=self.configFile)
        self.FileLineEdit.setText(self.FilePath)

        self.FileButton.clicked.connect(self.on_FileButton_clicked)

        self.setLayout(self.fileLayout)



    def on_FileButton_clicked(self):

        if self.type == 'file':
            fname = str(QtGui.QFileDialog.getOpenFileName(self, self.label,
                                                     self.FileLineEdit.text())[0])
        elif self.type == 'path':
            fname = str(QtGui.QFileDialog.getExistingDirectory(self, self.label,
                                                               self.FileLineEdit.text()))
            print(fname)
        if fname:

            self.setValue(fname)

    #### REQUIRED FUNCTIONS ####
    def changeConfigFile(self, file):
        self.configFile = file
        self.reset()

    def setValue(self, value):
        self.FileLineEdit.setText(value)

    def save(self):
        self.set(self.getValue(), config_file_path=self.configFile)
        return self.getValue()

    def reset(self):
        self.setValue(self.get(config_file_path=self.configFile))

        return self.getValue()

    def getValue(self):
        return self.FileLineEdit.text()

#### RAW EDIT WIDGET ####
class RawEditWidget(QtGui.QWidget):
    """
        RawEditWidget

        must supply config_file
        """

    def __init__(self, config_file, parent=None, **kwargs):
        super(type(self), self).__init__(**kwargs)

        self.configFile = config_file
        self.parent = parent
        ### TEXT EDIT ###
        self.textEdit = QtGui.QTextEdit(self)
        self.load_text()

        # set height restrictions
        self.fm = QFontMetrics(self.textEdit.font())
        #self.margin = [
        #    self.textEdit.textCursor().blockFormat().topMargin()*2,
        #    self.textEdit.textCursor().blockFormat().leftMargin() * 2
        #]
        self.margin = [10]*2 # its 5 on each side
        self.refresh_size()

        self.setWindowTitle("Editing  %s"%self.configFile)

        ### FOOTER ###
        self.saveButton = QtGui.QPushButton('Save')
        self.reloadButton = QtGui.QPushButton('Reload')
        self.exitButton = QtGui.QPushButton('Exit')

        # footer buttons event handling
        self.saveButton.clicked.connect(self.save_event)
        self.reloadButton.clicked.connect(self.load_text)
        self.exitButton.clicked.connect(self.close_event)

        self.footerLayout = QtGui.QHBoxLayout()
        self.footerLayout.setObjectName("footerLayout")
        self.footerLayout.addWidget(self.saveButton)
        self.footerLayout.addWidget(self.reloadButton)
        self.footerLayout.addWidget(self.exitButton)

        # set layout

        self.layout = QtGui.QVBoxLayout(self)

        self.layout.addWidget(self.textEdit)
        self.layout.addLayout(self.footerLayout)

        self.setLayout(self.layout)





    def refresh_size(self):
        split = self.plain.split('\n')
        self.textEdit.setMinimumHeight(self.margin[0]+self.fm.height()*len(split))
        self.textEdit.setMinimumWidth(self.margin[1]+max([self.fm.width(i) for i in split]))
    def load_text(self):
        self.textEdit.setText(
            IOTool._read_config_file(config_file_path=self.configFile)
        )
        self.plain = self.textEdit.toPlainText()

    def save_text(self):
        IOTool._write_config_file(
            self.textEdit.toPlainText(),
            config_file_path=self.configFile
        )
        self.load_text()

    ### EVENT STUFF ###
    def save_event(self):
        try:
            self.save_text()
        except:
            print(sys.exc_info())

        dia = QtGui.QMessageBox(self)
        dia.setWindowTitle("Save confirmation")
        dia.setText("Saved changes to %s"%self.configFile)
        dia.show()

    def close_event(self):
        if self.plain != self.textEdit.toPlainText():
            reply = QtGui.QMessageBox.question(self, 'Exit Confirmation','Unsaved data will be discarded. Continue?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
        if self.parent is not None:
            self.parent.reset()

        self.close()

    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Escape:
            self.close_event()
    def closeEvent(self, QCloseEvent):
        self.close_event()



#### MAIN WIDGET ####
class ConfigurationManager(QtGui.QWidget):

    def __init__(self, parent=None, **kwargs):
        super(ConfigurationManager, self).__init__(**kwargs)

        self.parent = parent
        self.title = "User Widget Manager"
        if "LabTools" in os.getcwd():
            # we are in LabTools
            widget_path = os.path.dirname(__file__)

            self.icon = os.path.abspath("../images/icon_normal_py3.png")
        else:
            cur_path = os.path.dirname(__file__)

            # find the path to the widgets folders
            widget_path = os.path.join(cur_path, "LabTools")

            self.icon = os.path.abspath("images/icon_normal_py3.png")

        self.setWindowIcon(QIcon(self.icon))
        self.setWindowTitle(self.title)
        ############# SETTING UI ###############

        # config file selector
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

        ### ALL SETTINGS WIDGET ###
        self.widgets = {}
        self.values = {}
        for name, data in IOTool.CONFIG_OPTIONS.items():
            if 'type' in data:
                if data['type'] == 'file' or data['type'] == 'path':
                    self.widgets[name] = FileWidget(name, data, self.configFilePath)
                elif data['type'] == 'selector' or data['type'] == 'selection':
                    self.widgets[name] = SelectorWidget(name, data, self.configFilePath)
                elif data['type'] == 'listview':
                    self.widgets[name] = ListViewWidget(name, data, self.configFilePath)
                else:
                    logging.info("%s has an invalid type: %s"%(name, data['type']))
            else:
                logging.info("%s has no type"%name)

            if name in self.widgets:
                self.values[name] = self.widgets[name].getValue()







        # footer buttons
        self.saveButton = QtGui.QPushButton('Save')
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.resetButton = QtGui.QPushButton('Reset')
        self.editButton = QtGui.QPushButton('Raw Edit')

        # footer buttons event handling
        self.saveButton.clicked.connect(self.save_event)
        self.refreshButton.clicked.connect(self.refresh_all)
        self.resetButton.clicked.connect(self.reset_all)
        self.editButton.clicked.connect(self.edit)

        self.footerLayout = QtGui.QHBoxLayout()
        self.footerLayout.setObjectName("footerLayout")
        self.footerLayout.addWidget(self.saveButton)
        self.footerLayout.addWidget(self.refreshButton)
        self.footerLayout.addWidget(self.resetButton)
        self.footerLayout.addWidget(self.editButton)





        # set the layout
        self.layout = QtGui.QVBoxLayout(self)
        # FORM LAYOUT self.layout = QtGui.QFormLayout(self)

        # add widgets to layout
        self.layout.addLayout(self.configfileLayout)

        for name, widget in self.widgets.items():
            self.layout.addWidget(widget)

        self.layout.addLayout(self.footerLayout)


        self.setLayout(self.layout)

        self.edit = None # so it doesnt automatically close

    def get_config_userwidget_setting(self):
        return IOTool.get_user_widgets(config_file_path=self.configFilePath)

    def set_config_file_name(self, fname):
        self.configFilePath = fname
        self.configFileLineEdit.setText(self.configFilePath)
        self.reset_all()

    def save_userwidget_selection(self):
        selected_widgets = []
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected_widgets.append(item.data())
        IOTool.set_user_widgets(selected_widgets)



    def refresh_all(self): # also an event
        self.refresh_subwidgets()

    def reset_all(self):
        self.reset_subwidgets()
        self.edit = None
    def reset(self):
        # called from RawEdit
        self.reset_all()
    def refresh_subwidgets(self):
        for name, widget in self.widgets.items():
            widget.setValue(self.values[name])

    def reset_subwidgets(self):
        for name, widget in self.widgets.items():
            widget.changeConfigFile(self.configFilePath)
            self.values[name] = widget.getValue()


    def set_parent(self, new_parent):
        self.parent = new_parent

    ### EVENT STUFF ###
    def change_active_widgets(self, *args, **kwargs):
        print("Active widget changed")
        print(*args)
        print(kwargs)
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

    def save(self):
        for name, widget in self.widgets.items():
            self.values[name] = widget.save()

    def save_event(self):
        self.save()
        if self.parent is None:
            dia = QtGui.QMessageBox(self)
            dia.setWindowTitle("Save confirmation")
            dia.setText("Saved! Restart LabGUI to see changes.")
            dia.show()
        else:
            self.parent.relaunch(force=True)

    def edit(self):
        try:
            if self.edit is not None:
                if self.edit.isEnabled():
                    self.edit.focusWidget()
                    return
            self.edit = RawEditWidget(self.configFilePath, self)
            self.edit.setWindowIcon(self.windowIcon())
            self.edit.show()
        except:
            print(sys.exc_info())
        # open new widget that modifies text of config.txt

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    #ex = RawEditWidget(IOTool.CONFIG_FILE_PATH)
    #ex.show()

    ex = ConfigurationManager()
    ex.show()
    #fileWidget = FileWidget(IOTool.SAVE_DATA_PATH_ID, IOTool.CONFIG_OPTIONS[IOTool.SAVE_DATA_PATH_ID], IOTool.CONFIG_FILE_PATH)

    #fileWidget.show()
    sys.exit(app.exec_())