"""
Created July 3rd, 2019

@author: zackorenberg

Create/Load data and/or notes
"""

import sys

from types import MethodType

from LocalVars import USE_PYQT5

import logging

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
        # TODO: implement?
        valueChanged = pyqtSignal()

    def __init__(self, parent=None, name='Data', line_num=0):
        super(SingleLineWidget, self).__init__()
        self.parent = parent

        self.name = name
        self.line = line_num

        # label
        self.label = QtGui.QLabel()
        self.label.setText(name)

        # lineedit
        self.line_edit = QtGui.QLineEdit()

        # make friends
        self.label.setBuddy(self.line_edit)

        # make delete button
        self.delete = QtGui.QPushButton()
        self.delete.setText("x")
        self.delete.setFixedWidth(20)
        #self.delete.setFixedHeight(20)
        #self.delete.setStyleSheet("QPushButton {background-color: red;}")



        # set event

        self.delete.clicked.connect(self.self_destruct)



        # make and set layout
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.delete)

        self.setLayout(self.layout)


    def update_line_number(self, line):
        self.line = line

    def get_tuple(self):
        if self.line_edit.text():
            return (self.name, self.line_edit.text())

    def get_data(self):
        if self.line_edit.text():
            return self.line_edit.text()

    def set_data(self, data):
        self.line_edit.setText(data)

    def self_destruct(self):
        if self.parent is not None:
            self.parent.remove_line(self.line)
        self.close()



class UserDataWidget(QtGui.QWidget):
    """a QWidget to manage user variables

    contains ways to add SingleLineWidgets and to fetch their values through
    emission of a SIGNAL that can be processed by listeners

    """

    if USE_PYQT5:

        updateUserVariables = pyqtSignal('PyQt_PyObject')

        loadUserVariables = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None, load_fname='5'):
        super(UserDataWidget, self).__init__(parent)

        # important variables
        self.lines = [] # stores SingleLineWidgets
        self.names = ["notes"]


        # Create
        self.create_line_layout()
        self.create_addrm_layout()
        self.create_notes_textedit()
        self.create_footer_layout()


        self.layout = QtGui.QVBoxLayout(self)

        # add layouts
        self.layout.addLayout(self.line_layout)
        self.layout.addLayout(self.addrm_layout)

        self.layout.addWidget(self.notes)
        self.layout.addLayout(self.footer_layout)


        # set layout
        self.setLayout(self.layout)



        # size policy
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                             QtGui.QSizePolicy.Minimum))

    #### CREATE QT ELEMENTS

    def create_line_layout(self):
        self.line_layout = QtGui.QVBoxLayout()

        # so its tight
        self.line_layout.setContentsMargins(0,0,0,0)
        self.line_layout.setSpacing(0)

    def create_addrm_layout(self):
        self.addrm_layout = QtGui.QHBoxLayout()

        self.bt_add = QtGui.QPushButton(self)
        self.bt_add.setText("Add Variable")
        self.bt_add.clicked.connect(self.bt_add_click)

        self.bt_rm = QtGui.QPushButton(self)
        self.bt_rm.setText("Remove last variable")
        self.bt_rm.clicked.connect(self.bt_rm_click)

        self.addrm_layout.addWidget(self.bt_add)
        self.addrm_layout.addWidget(self.bt_rm)


    def create_notes_textedit(self):
        self.notes = QtGui.QTextEdit()


        self.notes.setPlaceholderText("Notes...")

    def create_footer_layout(self):
        self.footer_layout = QtGui.QHBoxLayout()

    # Create variable function
    def new_line(self):
        text, okPressed = QtGui.QInputDialog.getText(self, "New Data", "Data Name:", QtGui.QLineEdit.Normal, "")
        if okPressed and text != "":
            ret = self.create_line(text)
            if ret is False:
                QtGui.QMessageBox.information(self, "Unable to create new data", "Data of same name already exists!")


    def create_line(self, name):
        if name not in self.names:
            widget = SingleLineWidget(self, name, len(self.lines))

            self.lines.append(widget)
            self.names.append(name)
            self.line_layout.addWidget(widget)

            return widget
        else:
            return False

    def remove_line(self, id):
        if id >= 0 and id < len(self.lines):
            self.line_layout.removeWidget(self.lines[id])
            self.lines[id].close()
            del self.lines[id]
            del self.names[id]
            self.update_lines()
        else:
            logging.debug("Incorrect index %s for data line"%str(id))
    def remove_line_last(self):
        self.line_layout.removeWidget(self.lines[-1])
        self.lines[-1].close()
        del self.lines[-1]
        del self.names[-1]
        self.update_lines()

    def remove_line_all(self):
        for widget in self.lines:
            self.line_layout.removeWidget(widget)
            widget.close()

        self.lines = []
        self.names = ["notes"]

    def update_lines(self):
        for i, widget in enumerate(self.lines):
            widget.update_line_number(i)
    ### EVENTS

    def bt_add_click(self):
        self.new_line()

    def bt_rm_click(self):
        self.remove_line_last()


    def get_user_data(self):
        ret = {}
        for line in self.lines:
            name, data = line.get_tuple()
            ret[name] = data
        if self.notes.toPlainText() != "":
            ret["notes"] = self.notes.toPlainText()
        return ret

    def set_user_data(self, obj):
        self.remove_line_all()
        for name, data in obj.items():
            if name == "notes":
                self.notes.setPlainText(data)
            else:
                try:
                    self.create_line(name).set_data(data)
                except:
                    logging.debug("Two data points of same name %s?"%name)
        self.update_lines()

    def set_user_data_parse(self, arr):
        """
        :param arr: type list, read from header of data file
        :return: nuthin
        """
        obj = {}
        for item in arr:
            obj[item[0].strip("'")] = item[1].strip("'")
        self.set_user_data(obj)


### NOT USED
def get_user_data(parent, variables_dict):
    """
    called the method of the datataker to update the dict structure containing
    the variables information
    """
    parent.datataker.update_user_variables(variables_dict)


def set_user_data(parent, variables_dict):
    """
    called the method of the datataker to update the dict structure containing
    the variables information
    """
    parent.datataker.update_user_variables(variables_dict)
    parent.widgets['userDataWidget'].loadUserVariables.emit(parent.datataker.user_data)



def add_widget_into_main(parent):
    """fonction to insert this widget into LabGui main window
    """
    mywidget = UserDataWidget(parent=parent)
    userDataDockWidget = QtGui.QDockWidget("User Data", parent)
    userDataDockWidget.setObjectName("userDataDockWidget")
    userDataDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    userDataDockWidget.setWidget(mywidget)

    parent.widgets["userDataWidget"] = mywidget
    parent.addDockWidget(Qt.RightDockWidgetArea, userDataDockWidget)

    parent.windowMenu.addAction(userDataDockWidget.toggleViewAction())

    # by default it will be hidden
    userDataDockWidget.hide()

    # add a method to the 'parent' instance
    # depending on the python version this fonction take different arguments
    parent.get_user_data = mywidget.get_user_data
    parent.set_user_data = mywidget.set_user_data
    # if sys.version_info[0] > 2:
    #
    #     parent.get_user_data = MethodType(mywidget.get_user_data,
    #                                       parent)
    #     parent.set_user_data = MethodType(mywidget.set_user_data,
    #                                       parent)
    # else:
    #
    #     parent.get_user_data = MethodType(mywidget.get_user_data,
    #                                       parent,
    #                                       parent.__class__)
    #
    #     parent.set_user_data = MethodType(mywidget.set_user_data,
    #                                       parent,
    #                                       parent.__class__)
    if USE_PYQT5:
        parent.widgets['userDataWidget'].loadUserVariables.connect(parent.widgets['userDataWidget'].set_user_data)
    # connect a trigger to that method
    # if USE_PYQT5:
    #
    #     parent.widgets["userVariableWidget"].updateUserVariables.connect(
    #         parent.get_user_data)
    #
    # else:
    #
    #     parent.connect(parent.widgets["userVariableWidget"],
    #                    SIGNAL("updateUserVariables(PyQt_PyObject)"),
    #                    parent.get_user_data)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = UserDataWidget()
    ex.show()
    sys.exit(app.exec_())
