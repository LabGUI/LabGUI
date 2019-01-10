# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 23:24:14 2017

@author: pfduc
"""


import sys

from importlib import import_module


from PyQt4.QtGui import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,\
    QPlainTextEdit, QPushButton, QComboBox, QPalette, QColor, QDockWidget

from PyQt4.QtCore import SIGNAL, Qt


import LabDrivers.utils as utils


class SimpleConnectWidget(QWidget):
    """
    this widget displays a combobox with a list of instruments which the
    user can connect to, it also has a refresh button
    """

    def __init__(self, parent=None):
        super(SimpleConnectWidget, self).__init__(parent)

        # main layout of the form is the verticallayout

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # moved the script stuff to a separate widget that lives in the toolbar

        self.labelLayout = QHBoxLayout()
        self.labelLayout.setObjectName("labelLayout")

        self.portLabel = QLabel(self)
        self.portLabel.setText("Availiable Ports")
        self.instrLabel = QLabel(self)
        self.instrLabel.setText("Instruments")

        self.labelLayout.addWidget(self.portLabel)
        self.labelLayout.addWidget(self.instrLabel)

        self.verticalLayout.addLayout(self.labelLayout)

        self.ports = QComboBox(self)
        self.ports.addItems(utils.refresh_device_port_list())
        self.ports.setObjectName("cbb_ports")

        self.instruments = QComboBox(self)
        self.instruments.addItems(utils.list_drivers(interface="real")[0])
        self.ports.setObjectName("cbb_instrs")

        self.cbbLayout = QHBoxLayout()
        self.cbbLayout.setObjectName("cbbLayout")

        self.cbbLayout.addWidget(self.ports)
        self.cbbLayout.addWidget(self.instruments)

        self.verticalLayout.addLayout(self.cbbLayout)

        self.connectButton = QPushButton(self)
        self.connectButton.setText("Connect the instrument")
        self.connectButton.setObjectName("connectButton")

        self.refreshButton = QPushButton(self)
        self.refreshButton.setText("refresh the port list")
        self.refreshButton.setObjectName("refreshButton")

        self.verticalLayout.addWidget(self.connectButton)
        self.verticalLayout.addWidget(self.refreshButton)
        self.headerTextEdit = QPlainTextEdit("")
        fontsize = self.headerTextEdit.fontMetrics()

        pal = QPalette()
        textc = QColor(245, 245, 240)
        pal.setColor(QPalette.Base, textc)
        self.headerTextEdit.setPalette(pal)
        # d3d3be
#        self.headerTextEdit.ba
        self.headerTextEdit.setFixedHeight(fontsize.lineSpacing() * 8)
        self.verticalLayout.addWidget(self.headerTextEdit)

        # moved the start stop button to the toolbar only

        self.setLayout(self.verticalLayout)

        self.connect(self.connectButton, SIGNAL(
            'clicked()'), self.on_connectButton_clicked)
        self.connect(self.refreshButton, SIGNAL(
            'clicked()'), self.on_refreshButton_clicked)

    def on_connectButton_clicked(self):
        """Connect a given instrument through a given port"""
        port = self.ports.currentText()
        instrument_name = self.instruments.currentText()

        # load the module which contains the instrument's driver
        if __name__ == "__main__":

            class_inst = import_module(instrument_name)

        else:

            class_inst = import_module(
                "." + instrument_name, package=utils.LABDRIVER_PACKAGE_NAME)
        msg = ""
#        msg.append("example")
#        msg.append("</span>")
        self.headerTextEdit.appendHtml(msg)
#        self.headerTextEdit.appendPlainText(msg)
        try:

            i = class_inst.Instrument(port)
            self.headerTextEdit.appendPlainText("%s" % (i.identify()))
            self.headerTextEdit.appendHtml(
                "The connection to the instrument %s through the port \
%s <span style=\" color:#009933;\" >WORKED</span>\n" % (instrument_name, port))

            i.close()

        except:

            self.headerTextEdit.appendHtml(
                "The connection to the instrument %s through the port\
%s <span style=\" color:#ff0000;\" >FAILED</span>\n" % (instrument_name, port))

    def on_refreshButton_clicked(self):
        """Refresh the list of the availiable ports"""
        self.ports.clear()
        self.ports.addItems(utils.refresh_device_port_list())


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = SimpleConnectWidget(parent=parent)

    # create a QDockWidget
    simpleconnectDockWidget = QDockWidget("Simple instrument console",
                                          parent)
    simpleconnectDockWidget.setObjectName("simpleConnectWidgetDockWidget")
    simpleconnectDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['ConnectTerminalWidget'] = mywidget

    simpleconnectDockWidget.setWidget(mywidget)
    parent.addDockWidget(Qt.RightDockWidgetArea, simpleconnectDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(simpleconnectDockWidget.toggleViewAction())
    simpleconnectDockWidget.hide()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = SimpleConnectWidget()
    ex.show()
    sys.exit(app.exec_())
