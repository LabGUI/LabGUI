"""
Created Aug 13th, 2019

@author: zackorenberg

This widget allows the user to set a default Remote Enable State, as well as assert specific modes to specific devices in real time
"""

import sys

from types import MethodType
import logging

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtCore as QtCore
    import PyQt5.QtWidgets as QtGui

else:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore

from LabTools.Display import QtTools

REN_MODES = [ # index corresponds to mode for GPIB device
    'Deassert Remote Enable',
    'Assert Remote Enable',
    'Deassert REN, Go To Local',
    'Assert REN, Address Device',
    'Assert Local Lockout, Address Device',
    'Assert Local Lockout. Allow RWLS',
    'Go To Local'
]

ENABLE_TEXT = "Send"
SET_DEFAULT = "Set Default"
UNSET_DEFAULT = "Unset Default"
SCROLLABLE = False
DEBUG = False
class REN_Default(QtGui.QWidget):
    def __init__(self, default=None, parent=None):
        super(REN_Default, self).__init__()
        self.parent = parent
        self.default = None

        self.hLayout = QtGui.QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtGui.QLabel("Default Mode:")
        self.state = QtGui.QLabel()
        self.btn = QtGui.QPushButton()

        self.btn.setText("Clear")
        self.btn.clicked.connect(self.btn_click)

        self.hLayout.addWidget(self.label)
        self.hLayout.addWidget(self.state)
        self.hLayout.addWidget(self.btn)

        self.setLayout(self.hLayout)

        self.set_default(default)



    def set_default(self, default):
        self.default = default

        if self.default is None:
            self.btn_disable()
            self.state.setText("None")
        else:
            self.btn_enable()
            self.state.setText("REN Mode %d"%self.default)

    def btn_click(self, *args, **kwargs):
        if self.parent is not None:
            self.parent.unset_all()

        self.btn_disable()


    def btn_enable(self):
        self.btn.setEnabled(True)

    def btn_disable(self):
        self.btn.setEnabled(False)


class REN_State(QtGui.QWidget):
    def __init__(self, REN_MODE, default=False, parent=None):
        super(REN_State, self).__init__()
        self.REN = int(REN_MODE)
        self.is_default = default
        self.parent = parent

        if self.REN < len(REN_MODES):
            self.REN_info = REN_MODES[self.REN]



        self.layout = QtGui.QHBoxLayout(self)


        self.inp_REN = QtGui.QLabel(str(self.REN))
        self.inp_info = QtGui.QLabel(self.REN_info)
        self.but_send = QtGui.QPushButton()
        self.but_default = QtGui.QPushButton()

        self.layout.addWidget(self.inp_REN)
        self.layout.addWidget(self.inp_info)
        self.layout.addStretch()
        self.layout.addWidget(self.but_send)
        self.layout.addWidget(self.but_default)

        #self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)


        # not necessarily required, but is here for failsafe
        self.setLayout(self.layout)

        self.but_send.setText(ENABLE_TEXT)

        if self.is_default:
            self.but_default.setText(UNSET_DEFAULT)
        else:
            self.but_default.setText(SET_DEFAULT)


        self.but_default.clicked.connect(self.btn_default_clicked)
        self.but_send.clicked.connect(self.btn_send_clicked)


        #self.setFixedSize(self.width(), self.height())

    def set_default(self):
        if self.parent is not None:
            self.parent.set_default(self.REN, from_widget=True)
            self.default_state(True) # this will run after parent.set_default is run

    def unset_default(self):
        if self.parent is not None:
            self.parent.unset_default(self.REN, from_widget=True)
            self.default_state(False) # this will run after parent.unset_default is run

    def toggle_default(self):
        if self.is_default:
            self.unset_default()
        else:
            self.set_default()


    def default_state(self, state=False): # True or False
        if state is True:
            self.is_default = True
            self.but_default.setText(UNSET_DEFAULT)
        elif state is False:
            self.is_default = False
            self.but_default.setText(SET_DEFAULT)

    def btn_default_clicked(self, *args, **kwargs):
        if self.but_default.text() == UNSET_DEFAULT:
            self.unset_default()
        elif self.but_default.text() == SET_DEFAULT:
            self.set_default()

    def btn_send_clicked(self, *args, **kwargs):
        if self.parent is not None:
            self.parent.send_mode(self.REN)

class REN_Widget(QtGui.QWidget):
    """This class is a TextEdit with a few extra features"""

    def __init__(self, parent=None):
        super(REN_Widget, self).__init__()

        # aesthetic stuff
        self.setWindowTitle("Remote Enable Widget")
        self.resize(500, 250)

        self.instrument_list = {}
        self.sanitized_list = list()  # tuple, (name, port, object)


        self.default_ren = None

        self.default_widget = REN_Default(self.default_ren, self)

        if parent is not None:
            self.parentClass = parent
            self.instr_hub = parent.instr_hub
        else:
            self.parentClass = None
            self.instr_hub = None

        self.deviceComboBox = QtGui.QComboBox()
        #self.deviceComboBox.activated[str].connect(self.change_device)

        self.REN_Lines = []
        for i in range(len(REN_MODES)):
            default_mode = False
            if self.default_ren == i:
                default_mode = True
            self.REN_Lines.append(REN_State(i, default_mode, self))


        # output console
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.addWidget(self.default_widget)
        self.verticalLayout.addWidget(self.deviceComboBox)
        if SCROLLABLE:
            # create scrollarea for stacked:
            self.scrollarea = QtGui.QScrollArea()
            self.scrollLayout = QtGui.QVBoxLayout()
            self.scrollLayout.setSpacing(0)
            self.scrollLayout.setContentsMargins(0,0,0,0)
            for state in self.REN_Lines:
                self.scrollLayout.addWidget(state)
            self.scrollwidget = QtGui.QWidget()
            self.scrollwidget.setLayout(self.scrollLayout)
            self.scrollarea.setWidget(self.scrollwidget)
            self.verticalLayout.addWidget(self.scrollarea)  # instead of stacked
        else:
            # self.verticalLayout.addStretch()
            for state in self.REN_Lines:
                self.verticalLayout.addWidget(state)
            # self.verticalLayout.addStretch()
 #       #self.footer = self.create_footer()
##        self.verticalLayout.addLayout(self.footer)

        self.setLayout(self.verticalLayout)

    def send_mode(self, mode):
        instr = self.current_instrument()

        if instr is not None:
            instr.set_ren(mode)

    def set_default(self, mode, from_widget = False):
        if self.default_ren != mode and self.default_ren is not None:
            self.REN_Lines[self.default_ren].default_state(False)
        self.default_ren = mode
        self.default_widget.set_default(mode)
        # TODO: add stuff to change default text
        if not from_widget:
            for i in range(len(REN_MODES)):
                if self.default_ren != i:
                    self.REN_Lines[i].default_state(False)
                else:
                    self.REN_Lines[i].default_state(True)
        else:
            self.save_default()

    def unset_default(self, mode, from_widget = False):
        if self.default_ren == mode:
            self.default_ren = None
            self.default_widget.set_default(None)
            # TODO: add stuff to change default text
        if not from_widget:
            for i in range(len(REN_MODES)):
                self.REN_Lines[i].default_state(False)
        else:
            self.save_default()

    def unset_all(self, from_widget = False):
        self.default_ren = None
        for state in self.REN_Lines:
            state.default_state(False)

        self.default_widget.set_default(None)

        if from_widget:
            self.save_default()

    def save_default(self):
        if self.parentClass is not None:
            self.parentClass.save_ren()


    # following two functions are used from LabGui.py to load/save defaults
    def get_ren(self):
        return self.default_ren

    def set_ren(self, level):
        if level is None or level == 'None':
            self.default_ren = None
            self.unset_all()
        else:
            self.set_default(int(level)) # this will automatically update default_ren, as well as unsetting all


    ##### DEVICE DROPBOX STUFF #####
    def enterEvent(self, event):
        # keep list updated
        self.update_devices()

    def update_instrument_list(self):
        if self.parentClass is not None:
            self.instrument_list = self.parentClass.instr_hub.get_instrument_list()
            #print(self.instrument_list)

            #print(self.parentClass.instr_hub.get_port_param_pairs())
            #print(self.parentClass.instr_hub.get_instrument_nb())

            z = self.instrument_list.items()

            ports = list()
            instruments = list()
            names = list()
            for x, y in z:
                if x is not None and "ComputerTime" not in x:
                    ports.append(x)
                    instruments.append(self.instrument_list[x])
                    names.append(self.instrument_list[x].ID_name)
                    #print(x,self.instrument_list[x].ID_name)
            self.sanitized_list = list(zip(names, ports, instruments))
            return

    def update_devices(self):
        # going need to get get_instrument_list
        self.update_instrument_list()
        text = self.deviceComboBox.currentText() # to set back to
        self.deviceComboBox.clear()
        for tuples in self.sanitized_list:
            self.deviceComboBox.addItem(tuples[0]+" on "+tuples[1])
        # now time to set current choice if it is still in the list
        index = self.deviceComboBox.findText(text)
        if index != -1:
            self.deviceComboBox.setCurrentIndex(index)


    def current_instrument(self):
        idx = self.deviceComboBox.currentIndex()
        if 0 <= idx < len(self.sanitized_list):
            return self.sanitized_list[idx][2] # this should be instrument
        else:
            return None


def add_widget_into_main(parent):
    #return #we dont want this to happen yet
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = REN_Widget(parent)

    # create a QDockWidget
    propDockWidget = QtGui.QDockWidget("Remote Enable", parent)
    propDockWidget.setObjectName("RENWidget")
    propDockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        | QtCore.Qt.BottomDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['RENWidget'] = mywidget

    propDockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, propDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(propDockWidget.toggleViewAction())

    # redirect print statements to show a copy on "console"
    sys.stdout = QtTools.printerceptor(parent)

    propDockWidget.resize(500,250)
    if not DEBUG:
        propDockWidget.hide()


if __name__ == "__main__":

    try:
        app = QtGui.QApplication(sys.argv)
        ex = REN_Widget()
        #ex = DevicePropertyWidget("AH", {}, debug=True)
        ex.show()
        #print(ex.get_properties())
        sys.exit(app.exec_())
    except:
        print(sys.exc_info())