# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 23:24:14 2017

@author: pfduc
"""


from LabDrivers import Tool
import sys
import socket
import numpy as np

from LocalVars import USE_PYQT5

if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui

    from PyQt5.QtCore import Qt, pyqtSignal, QMutex, QThread

else:

    import PyQt4.QtGui as QtGui

    from PyQt4.QtCore import Qt, SIGNAL, QMutex, QThread


CLIENT = '132.206.186.166'
HOST = '132.206.186.166'  # Symbolic name meaning all available interfaces
PORT = 48372


class DataServer(QThread):
    """
        allows to communicate with instruments connected to other computers
        the user can use the same methods as defined in the instrument class
        and the server will call these methods and return any output to the
        client.

        The client is restricted to one for the moment (the connection can occur
        but no data will be sent back if the client doesn't match CLIENT)
    """

    def __init__(self, mutex, parent=None, instrument_hub=None,
                 debug=False, host=None, port=None):

        super(DataServer, self).__init__(parent)

        self.mutex = mutex

        # to be able to run in debug mode (ie without physical connections)
        self.DEBUG = debug

        # if host is unspecified use the default
        if host == None:

            self.host = HOST

        else:

            self.host = host

        # if port is unspecified use the default
        if port == None:

            self.port = PORT

        else:

            self.port = port

        # the data server is linked to an instrument hub
        self.instr_hub = instrument_hub

        if USE_PYQT5:

            self.instr_hub.instrument_hub_connected.connect(self.reset_lists)

            parent.serverOver.connect(self.stop)

        else:

            self.connect(self.instr_hub, SIGNAL(
                "instrument_hub_connected()"), self.reset_lists)

            self.connect(parent, SIGNAL("ServerOver()"), self.stop)

        self.instruments = None
        self.port_param_pairs = None

        self.stopped = False

    def run(self):

        print("start server @%s:%s" % (self.host, self.port))
        self.stopped = False

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("init socket")

        serversocket.bind((HOST, PORT))
        print("ready to listen")

        serversocket.listen(5)

        # listen to request until stopped by the user
        while not self.stopped:

            print("in the loop", self.stopped)
            # accept connections from outside

            try:

                (clientsocket, address) = serversocket.accept()
                print("recieved a request from %s" % address[0])

            except socket.timeout:
                print("Socket timeout")
                address = ""

            if CLIENT in address:

                while 1:
                    try:
                        req = clientsocket.recv(1024)

                        # if the request isn't an empty string
                        if req:

                            self.mutex.lock()

                            # manage the request
                            answer = self.manage_request(req)

                            # sends the output of the instrument
                            clientsocket.send(str(answer))

                            self.mutex.unlock()
                        else:

                            break

                    except IOError:

                        break

        self.stopped = True
        self.completed = False
        print("Server is Over")

    def stop(self):
        self.stopped = True

    def isStopped(self):
        return self.stopped

    def reset_lists(self):
        """
            If changes are made to the InstrumentHub, the DataServer will not acknowledge them
            unless using this method
        """
        self.instruments = self.instr_hub.get_instrument_list()
        self.instruments.pop(None)
        self.port_param_pairs = self.instr_hub.get_port_param_pairs()

        for port_param_pair in self.port_param_pairs:
            port = port_param_pair[0]
            param = port_param_pair[1]
            try:
                name = "%s.%s" % (self.instruments[port].ID_name, param)
            except KeyError:
                print(self.instruments[port].ID_name, param)
                print(port)

    def manage_request(self, client_request):

        print("client_request", client_request)

        # default answer
        answer = np.nan

        # the request should be in the format
        # "inst_ID.method(*args,**kwargs)@device_port"
        try:

            id_name, method = client_request.split('.')

        except ValueError:

            print("The client request '%s' doesn't match the pattern : %s" % (
                client_request, "inst_ID.method(*args,**kwargs)@device_port"))
            return answer

        # the request should be in the format
        # "inst_ID.method(*args,**kwargs)@device_port"
        try:

            method, device_port = method.split('@')

        except ValueError:

            print("The client request '%s' doesn't match the pattern : %s" % (
                client_request, "inst_ID.method(*args,**kwargs)@device_port"))
            return answer

        try:

            method, s = method.split('(')

        except ValueError:

            print("The client request '%s' doesn't match the pattern : %s" % (
                client_request, "inst_ID.method(*args,**kwargs)@device_port"))
            return answer

        # s should be like "*args,**kwargs)", so we get rid of the ')'
        s = s[: -1]

        # populate the args and kwargs to pass them as arguments of the method
        args = ()
        kwargs = {}

        for arg in s.split(','):

            # if there is an '=' it is a keyword argument
            if '=' in arg:

                key, val = arg.split('=')
                kwargs[key] = val

            else:

                args = args + (arg,)

        # see if the requested instrument is connected to the server
        if id_name in self.instruments[device_port].ID_name:

            try:
                # fetch the method of the connected instrument, ie, the
                # the method must be defined in the class of the the
                # instrument one connected to the server
                method = getattr(self.instruments[device_port], method)

                # pass the arguments
                answer = method(*args, **kwargs)

            except AttributeError as e:
                # return a comprehensive error message
                answer = "%s:%s" % ('AttributeError', e.message)

            except TypeError as e:
                # return a comprehensive error message
                answer = "%s:%s" % ('TypeError', e.message)

        return answer


class ServerWidget(QtGui.QWidget):
    """
    this widget displays a combobox with a list of instruments which the
    user can connect to, it also has a refresh button
    """

    if USE_PYQT5:

        serverOver = pyqtSignal()

    def __init__(self, parent=None, debug=False):
        super(ServerWidget, self).__init__(parent)

        # main layout of the form is the verticallayout

        self.DEBUG = debug

        self.data_mutex = QMutex()

        try:

            instr_hub = parent.instr_hub

        except AttributeError:

            instr_hub = Tool.InstrumentHub(parent=self,
                                           debug=self.DEBUG)

        self.server = DataServer(self.data_mutex, parent=self,
                                 instrument_hub=instr_hub)

        # set the layout of the elements of the widget
        self.vlayout = QtGui.QVBoxLayout(self)

        # Introduction text
        hlayout = QtGui.QHBoxLayout()

        # the label in front of the line edit
        label = QtGui.QLabel(self)
        label.setText("This widget is used to communicate with the \n\
instruments connected in the instrument\n hub over IP address.")

        hlayout.addWidget(label)

        self.vlayout.addLayout(hlayout)

        # line 1, the host name
        hlayout = QtGui.QHBoxLayout()

        # the label in front of the line edit
        label = QtGui.QLabel(self)
        label.setText("Host:")

        # a line edit to write the host IP address
        self.le_host = QtGui.QLineEdit(self)
        self.le_host.setText(HOST)

#        self.connect(self.le_host,QtCore.SIGNAL("textEdited(QString)"),
#             self.le_host_edited)

        hlayout.addWidget(label)
        hlayout.addWidget(self.le_host)

        self.vlayout.addLayout(hlayout)

        # line 2, the port number
        hlayout = QtGui.QHBoxLayout()

        # the label in front of the line edit
        label = QtGui.QLabel(self)
        label.setText("Port:")

        # a line edit to write the host IP address
        self.le_port = QtGui.QLineEdit(self)
        self.le_port.setText(str(PORT))
#        self.connect(self.le_port,QtCore.SIGNAL("textEdited(QString)"),
#                     self.le_port_edited)

        hlayout.addWidget(label)
        hlayout.addWidget(self.le_port)

        self.vlayout.addLayout(hlayout)

        # line 3, start, stop server buttons
        hlayout = QtGui.QHBoxLayout()

        # a button to start the server
        self.bt_start_server = QtGui.QPushButton(self)
        self.bt_start_server.setText("Start Server")

        # a button to stop the server
        self.bt_stop_server = QtGui.QPushButton(self)
        self.bt_stop_server.setText("Stop Server")

        # assign triggers for the buttons
        if USE_PYQT5:

            self.bt_start_server.clicked.connect(
                self.on_bt_start_server_clicked)

            self.bt_stop_server.clicked.connect(
                self.on_bt_stop_server_clicked)

        else:

            self.connect(self.bt_start_server, SIGNAL(
                'clicked()'), self.on_bt_start_server_clicked)

            self.connect(self.bt_stop_server, SIGNAL(
                'clicked()'), self.on_bt_stop_server_clicked)

        hlayout.addWidget(self.bt_start_server)
        hlayout.addWidget(self.bt_stop_server)

        self.vlayout.addLayout(hlayout)

    def on_bt_start_server_clicked(self):
        """Start the server"""

        # fetch the IP written by the user
        host = str(self.le_host.text())

        try:
            # if the port is a number we initiate the server connection
            port = int(self.le_port.text())

        except ValueError:

            port = PORT

        self.server.host = host

        self.server.port = port

        self.server.start()

    def on_bt_stop_server_clicked(self):
        """Stop the server"""

        if USE_PYQT5:

            self.serverOver.emit()

        else:

            self.emit(SIGNAL("ServerOver()"))

#    def le_host_edited(self):
#        obj = self.sender()
#
#        print obj.text()
#
#    def le_port_edited(self):
#
#        obj = self.sender()
#
#        print obj.text()
#
#        int(obj.text())


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = ServerWidget(parent=parent)

    # create a QDockWidget
    simpleconnectDockWidget = QtGui.QDockWidget("Server",
                                                parent)
    simpleconnectDockWidget.setObjectName("serverWidgetDockWidget")
    simpleconnectDockWidget.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['ServerWidget'] = mywidget

    simpleconnectDockWidget.setWidget(mywidget)
    parent.addDockWidget(Qt.RightDockWidgetArea, simpleconnectDockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(simpleconnectDockWidget.toggleViewAction())
    simpleconnectDockWidget.hide()


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = ServerWidget()
    ex.show()
    sys.exit(app.exec_())
