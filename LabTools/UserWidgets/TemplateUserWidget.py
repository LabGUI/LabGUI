# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 23:24:14 2017

@author: pfduc
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


class ExampleWidget(QtGui.QWidget):
    """This example widget is used to showcase how to create custom widgets."""

    if USE_PYQT5:
        # creates two signals which will be emitted by the widget, we will
        # connect them with the parent of the widget as a listener in the
        # "add_widget_into_main" function (in that case it could also be
        # defined in the "__init__" method.
        # Note: it is important to define the signal at this level of the class
        sg_start_something = pyqtSignal()
        sg_stop_something = pyqtSignal()

    def __init__(self, parent=None, debug=False):
        super(ExampleWidget, self).__init__(parent)

        self.DEBUG = debug

        # set the layout of the elements of the widget
        self.vlayout = QtGui.QVBoxLayout(self)

        # line 1 of the vertical layout
        hlayout = QtGui.QHBoxLayout()

        # the label in front of the line edit
        label = QtGui.QLabel(self)
        label.setText("Label1:")

        # a line edit to write some text
        self.le_example = QtGui.QLineEdit(self)
        self.le_example.setText("Write some text...")

        hlayout.addWidget(label)
        hlayout.addWidget(self.le_example)

        self.vlayout.addLayout(hlayout)

        # line 2, start, stop buttons
        hlayout = QtGui.QHBoxLayout()

        # a button to start something
        self.bt_start = QtGui.QPushButton(self)
        self.bt_start.setText("Start")

        # a button to stop something
        self.bt_stop = QtGui.QPushButton(self)
        self.bt_stop.setText("Stop")

        # assign triggers for the buttons
        if USE_PYQT5:
            self.bt_start.clicked.connect(self.on_bt_start_clicked)
            self.bt_stop.clicked.connect(self.on_bt_stop_clicked)
        else:
            self.connect(
                self.bt_start,
                SIGNAL('clicked()'),
                self.on_bt_start_clicked
            )
            self.connect(
                self.bt_stop,
                SIGNAL('clicked()'),
                self.on_bt_stop_clicked
            )

        hlayout.addWidget(self.bt_start)
        hlayout.addWidget(self.bt_stop)

        self.vlayout.addLayout(hlayout)

    def on_bt_start_clicked(self):
        """Start something"""

        if USE_PYQT5:
            self.sg_start_something.emit()
        else:
            self.emit(SIGNAL("StartSomething()"))

    def on_bt_stop_clicked(self):
        """Stop the server"""

        if USE_PYQT5:
            self.sg_stop_something.emit()
        else:
            self.emit(SIGNAL("StopSomething()"))


def do_something_function(parent):
    """Definition of a method which will be assigned to LabGuiMain instance
    and connected to the sg_start_something signal"""

    # make sure the debug mode is set to True
    if not parent.DEBUG:
        parent.option_change_debug_state()

    # connect the instrument hub
    parent.connect_instrument_hub()

    # start the datataker
    parent.start_DTT()


def stop_things_function(parent):
    """Definition of a method which will be assigned to LabGuiMain instance
    and connected to sg_stop_something signal"""

    # stop the datataker
    parent.stop_DTT()


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain through this function
    create a QDock widget and store a reference to the widget in a dictionary
    """

    mywidget = ExampleWidget(parent=parent)
    widget_name = "ExampleWidget"

    # fill the dictionary with the ExampleWidget instance added into LabGuiMain
    parent.widgets[widget_name] = mywidget

    # create a QDockWidget
    dock_widget = QtGui.QDockWidget("Example", parent)
    dock_widget.setObjectName("exampleWidgetDockWidget")
    dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    dock_widget.setWidget(mywidget)
    parent.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    # Enable the toggle view action of this widget as a "window" menu option
    parent.windowMenu.addAction(dock_widget.toggleViewAction())
    dock_widget.hide()

    # assigning the method defined in this file to the parent class so we can
    # use them to setup signals between our ExampleWidget and LabGuiMain
    if sys.version_info[0] > 2:
        # python3
        parent.do_something = MethodType(do_something_function, parent)
        parent.stop_things = MethodType(stop_things_function, parent)

    else:
        # python2
        parent.do_something = MethodType(do_something_function, parent,
                                         parent.__class__)
        parent.stop_things = MethodType(stop_things_function, parent,
                                        parent.__class__)

    # now we connect these newly assigned methods of LabGuiMain to the signal
    # of our ExampleWidget (each added widgets will be in the self.widget
    # dictionary of LabGuiMain with key entry corresponding to the widget name
    # in this case it is "ExampleWidget"
    if USE_PYQT5:
        # Whenever the signal is triggered by ExampleWidget, the method
        # "do_something" of "LabGuiMain" will be called
        parent.widgets[widget_name].sg_start_something.connect(
            parent.do_something)

        # Whenever the signal is triggered by ExampleWidget, the method
        # "stop_things" of "LabGuiMain" will be called
        parent.widgets[widget_name].sg_stop_something.connect(
            parent.stop_things)
    else:
        parent.connect(parent.widgets[widget_name], SIGNAL(
            "StartSomething()"), parent.do_something)

        parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
            "StopSomething()"), parent.stop_thing)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = ExampleWidget()
    ex.show()
    sys.exit(app.exec_())
