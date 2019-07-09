# -*- coding: utf-8 -*-
"""
Created on Tue Jun 06 21:59:31 2017

Copyright (C) 10th april 2015 Pierre-Francois Duc
License: see LICENSE.txt file
"""


import sys

from types import MethodType

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtCore import Qt, pyqtSignal

else:

    import PyQt4.QtGui as QtGui
    from PyQt4.QtCore import Qt, SIGNAL


class SingleLineWidget(QtGui.QWidget):
    """a line of QWidget representing a user variable

    the line contains one line edit for the name, one for the value and
    one tick box to choose to update the variable or not

    """

    if USE_PYQT5:

        valueChanged = pyqtSignal('int')

    def __init__(self, parent=None, line_num=None):
        super(SingleLineWidget, self).__init__(parent)

        # give the line a number
        if not isinstance(line_num, int):

            self.line_num = 0

        else:

            self.line_num = line_num

        # create the 3 components of the line
        self.param_label_le = self.create_lineedit(
            label_text="Var%i name" % self.line_num)

        self.param_value_le = self.create_lineedit(
            label_text="Var%i value" % self.line_num)

        self.param_update_tb = self.create_tickbox()

        # create an horizontal layout
        self.horizontal_layout = QtGui.QHBoxLayout(self)

        # incorporate the 3 components into the layout
        self.horizontal_layout.addWidget(self.param_label_le)
        self.horizontal_layout.addWidget(self.param_value_le)
        self.horizontal_layout.addWidget(self.param_update_tb)

        self.setLayout(self.horizontal_layout)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                             QtGui.QSizePolicy.Minimum))
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

    def create_lineedit(self, label_text="Name"):
        """Create a line edit widget

        """
        le = QtGui.QLineEdit(self)

        le.setObjectName("param_name_le")

        # set up a signal to be triggered upon editing by a user
        le.textEdited.connect(self.lineEdit_handler)

        if isinstance(label_text, str):

            le.insert(label_text)

        return le

    def create_tickbox(self):
        """Create a tick box widget

        """
        tb = QtGui.QCheckBox(self)

        tb.setObjectName("checkBox")
        # set up a signal to be triggered upon ticking/unticking
        tb.stateChanged.connect(self.tickbox_handler)

        return tb

    def lineEdit_handler(self, string):
        """signal triggered upon editing by a user

        emit a signal with the line number        

        """
        if USE_PYQT5:

            self.valueChanged.emit(self.line_num)

        else:

            self.emit(SIGNAL("valueChanged(int)"), self.line_num)

    def tickbox_handler(self):
        """signal triggered upon ticking/unticking

        emit a signal with the line number

        """
        if USE_PYQT5:

            self.valueChanged.emit(self.line_num)

        else:

            self.emit(SIGNAL("valueChanged(int)"), self.line_num)


class UserVariableWidget(QtGui.QWidget):
    """a QWidget to manage user variables

    contains ways to add SingleLineWidgets and to fetch their values through
    emission of a SIGNAL that can be processed by listeners

    """

    if USE_PYQT5:

        updateUserVariables = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None, load_fname='5'):
        super(UserVariableWidget, self).__init__(parent)

        # main layout of the form is the vertical_layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.setObjectName("vertical_layout")

        # this will contain the buttons to generate/delete SingleLineWidget
        # instances and also a line edit to have the desired number of instances
        self.loadLayout = QtGui.QHBoxLayout()
        self.loadLayout.setObjectName("vertical_Layout")

        self.numVariableLabel = QtGui.QLabel(self)
        self.numVariableLabel.setText("Number of variables")

        # line edit to indicate how many lines to create
        self.numVariableLineEdit = QtGui.QLineEdit(self)
        self.numVariableLineEdit.setText(load_fname)

        # button to generate new lines
        self.generateVariableButton = QtGui.QPushButton(self)
        self.generateVariableButton.setText("Create variables")

        # button to delete unticked lines
        self.deleteVariableButton = QtGui.QPushButton(self)
        self.deleteVariableButton.setText("Delete unticked")
        self.deleteVariableButton.hide()

        # incorporate the components into the layout
        self.loadLayout.addWidget(self.numVariableLabel)
        self.loadLayout.addWidget(self.numVariableLineEdit)
        self.loadLayout.addWidget(self.generateVariableButton)
        self.loadLayout.addWidget(self.deleteVariableButton)

        self.vertical_layout.addLayout(self.loadLayout)

        # this will contain the SingleLineWidget instances
        self.line_layout = QtGui.QVBoxLayout()

        # this will contain the triggering button to send the ticked variables
        # names and values to some listeners
        self.updateVariableLayout = QtGui.QHBoxLayout()
        self.updateVariableLayout.setObjectName("updateVariableLayout")

        self.updateVariableButton = QtGui.QPushButton(self)
        self.updateVariableButton.setText("update variables")

        self.updateVariableLayout.addWidget(self.updateVariableButton)

        self.vertical_layout.addLayout(self.updateVariableLayout)

        self.setLayout(self.vertical_layout)

        # establishing the signal trigger within the class
        self.generateVariableButton.clicked.connect(
            self.on_generateVariableButton_clicked)

        self.deleteVariableButton.clicked.connect(
            self.on_deleteVariableButton_clicked)

        self.updateVariableButton.clicked.connect(
            self.on_updateVariableButton_clicked)

        self.lines = []

    def create_line(self, line_num=None):
        """create a new SingleLineWidget instance

            create the line, connect with a SIGNAL emitted by the latter
            add the line to the existing layout
        """
        new_line = SingleLineWidget(line_num=line_num)

        if USE_PYQT5:

            new_line.valueChanged.connect(self.value_changed)

        else:

            self.connect(new_line, SIGNAL("valueChanged(int)"),
                         self.value_changed)

        self.lines.append(new_line)
        self.line_layout.addWidget(new_line)

        return new_line

    def resetLayout(self):
        """reshuffle the layout component around so it looks nice
        """
        # delete the components of the layout
        for i in reversed(list(range(self.vertical_layout.count()))):

            item = self.vertical_layout.itemAt(i)
            self.vertical_layout.removeItem(item)

            try:

                item.setParent(None)

            except:

                pass

        # display this button only if there are lines to delete
        if self.lines:

            self.deleteVariableButton.show()

        else:

            self.deleteVariableButton.hide()

        # update the components of the layout with the new values
        self.vertical_layout.addLayout(self.loadLayout)
        self.vertical_layout.addLayout(self.line_layout)
        self.vertical_layout.addLayout(self.updateVariableLayout)

    def on_generateVariableButton_clicked(self):
        """action of the button

        this will create as many lines as in the numVariableLineEdit 
        """

        # if there already are some lines
        start_idx = len(self.lines)

        for i in range(int(self.numVariableLineEdit.text())):

            self.create_line(i + start_idx)

        self.resetLayout()

    def on_deleteVariableButton_clicked(self):
        """action of the button

        remove the SingleLineWidget whose tickbox are unticked
        """

        for wid in reversed(self.lines):

            if not wid.param_update_tb.isChecked():

                # remove the widget from the lines array
                self.lines.remove(wid)
                # remove the widget from the layout
                self.line_layout.removeWidget(wid)
                # terminate the widget
                wid.close()

            else:
                # only remove the widget from the layout
                self.line_layout.removeWidget(wid)

        # add the remaining widgets to the layout
        for i, line in enumerate(self.lines):

            # re index the line number
            line.line_num = i
            # add the widget to the layout
            self.line_layout.addWidget(line)

        # call the method to reset the layout
        self.resetLayout()

    def on_updateVariableButton_clicked(self):
        """action of the button

        gather the names and values of ticked variables and emits them inside
        a dict structure
        """
        adict = {}

        for line in self.lines:

            if line.param_update_tb.isChecked():

                key = str(line.param_label_le.text())
                value = str(line.param_value_le.text())


                adict[key] = value

        # send the signal with the dict
        if USE_PYQT5:

            self.updateUserVariables.emit(adict)

        else:

            self.emit(SIGNAL("updateUserVariables(PyQt_PyObject)"), adict)

        # the button is disabled to keep track of the data sent
        self.updateVariableButton.setEnabled(False)

    def value_changed(self, line_num):
        """
        triggered by changing a variable name or value or by (un)ticking the 
        tickbox on a line.

        I reenable the updateVariable button
        """
        if self.lines[int(line_num)].param_update_tb.isChecked():

            self.updateVariableButton.setEnabled(True)


def update_user_variables(parent, variables_dict):
    """
    called the method of the datataker to update the dict structure containing
    the variables information
    """
    parent.datataker.update_user_variables(variables_dict)


def add_widget_into_main(parent):
    """fonction to insert this widget into LabGui main window
    """
    mywidget = UserVariableWidget(parent=parent)
    userVariableDockWidget = QtGui.QDockWidget("Set user variables", parent)
    userVariableDockWidget.setObjectName("userVariableDockWidget")
    userVariableDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    userVariableDockWidget.setWidget(mywidget)

    parent.widgets["userVariableWidget"] = mywidget
    parent.addDockWidget(Qt.RightDockWidgetArea, userVariableDockWidget)

    parent.windowMenu.addAction(userVariableDockWidget.toggleViewAction())

    # by default it will be hidden
    userVariableDockWidget.hide()

    # add a method to the 'parent' instance
    # depending on the python version this fonction take different arguments
    if sys.version_info[0] > 2:

        parent.update_user_variables = MethodType(update_user_variables,
                                                  parent)

    else:

        parent.update_user_variables = MethodType(update_user_variables,
                                                  parent,
                                                  parent.__class__)

    # connect a trigger to that method
    if USE_PYQT5:

        parent.widgets["userVariableWidget"].updateUserVariables.connect(
            parent.update_user_variables)

    else:

        parent.connect(parent.widgets["userVariableWidget"],
                       SIGNAL("updateUserVariables(PyQt_PyObject)"),
                       parent.update_user_variables)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = UserVariableWidget()
    ex.show()
    sys.exit(app.exec_())
