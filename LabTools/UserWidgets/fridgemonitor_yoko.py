"""

Created on Jun 25 2019

Author: @zackorenberg

Fridge Monitor for Faraday Fridge w/o LakeShore, based on labgui Faraday Fridge Monitor from GervaisLabs, updated to Python3/PyQt5
"""
from __future__ import division
from LocalVars import USE_PYQT5
from collections import OrderedDict

if USE_PYQT5:
    from PyQt5 import QtCore
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtGui import QFont, QKeySequence

    QtGui.QFont = QFont
    Qt = QtCore.Qt
    # from PyQt5 import Qt
else:
    from PyQt4 import QtCore
    from PyQt4 import QtGui

import numpy as np
from matplotlib import dates
from matplotlib import ticker
import matplotlib.pyplot as plt

# This code relies on LabDrivers and LabTools from our LabGUI package
#from LabDrivers import LS370_janis
from LabDrivers import YOKOGS200
from LabDrivers import HP4263B
from LabDrivers import MKS146C

from LabTools.IO import IOTool
import time, datetime, sys, logging

from LabTools.Display.mplZoomWidget import MatplotlibZoomWidget
from LabTools.Display import QtTools

try:
    from LabTools.UserWidgets.fridgemonitor_parts import data_server, textmsg, ui_fridgemonitor
    from LabTools.UserWidgets.fridgemonitor_parts import fridgemonthread
    from LabTools.UserWidgets.fridgemonitor_parts import conversions
except ImportError:
    from fridgemonitor_parts import data_server, textmsg, ui_fridgemonitor
    from fridgemonitor_parts import fridgemonthread
    from fridgemonitor_parts import conversions

import numpy as np
from matplotlib import dates
from matplotlib import ticker
import matplotlib.pyplot as plt

DEBUG = False
# Changes to make:
# new file each day
# set history length
# show pressure
# show He and N2 levels
# different colours :)
#########################################
# The following is a list of allowed devices to obtain data. This list will be used
#  dynamically when the start button is pressed, matching any connected device to
#  a type from the following list. Note that it will only select one of the connected
#  devices, meaning that if, for example, there are both a LS370 and LS370_janis connected
#  the application will choose the first one connected, or last depending on var
HEATER_ALLOWED = ['YOKOGS200','YOKO']
CMN_ALLOWED = ['HP426B']
PIRANI_ALLOWED = ['MKS146C']
CHOOSE_FIRST_DEVICE = True


# Original definition
# self.lakeshore = FakeInstr()  # LS370_janis.Instrument('name', debug=True)
# self.CMN = FakeInstr()  # HP4263B.Instrument('name', debug=True)
# self.pirani = FakeInstr()  # MKS146C.Instrument('name', debug=True)
# add print function
# Add conversion to temperature
# Add helium level meter support
# add pressure gauge reading


class MiniPlot(QtGui.QFrame):
    ''' This class is for each of the panels in the fridgemonitor
    It includes the main plot and a few checkboxes to change settings '''

    def __init__(self, label_text='Therm', parent=None):
        super(MiniPlot, self).__init__()
        self.parent = parent
        # style sheet is used to make the darker grey background
        self.setStyleSheet("background-color: rgb(190,190,190); ")

        # this is the lefthand part with the numerical display and the checkboxes
        self.v_layout = QtGui.QVBoxLayout()

        # The name of the thermometer/sensor goes here
        self.label = QtGui.QLabel(label_text)
        self.label.setFont(QtGui.QFont("Arial", 12))
        self.v_layout.addWidget(self.label)

        # the raw value (ohms etc.) goes here
        self.display_label = QtGui.QLabel("", )
        self.display_label.setAlignment(Qt.AlignHCenter)
        self.display_label.setFont(QtGui.QFont("Arial", 12))
        self.display_label.setStyleSheet("background-color: rgb(250,190,190); ")
        self.v_layout.addWidget(self.display_label)

        # the converted temperature value goes here
        self.T_label = QtGui.QLabel("", )
        self.T_label.setAlignment(Qt.AlignHCenter)
        self.T_label.setFont(QtGui.QFont("Arial", 12))
        self.T_label.setStyleSheet("background-color: rgb(250,190,190); ")
        self.v_layout.addWidget(self.T_label)

        # whether to plot in raw (ohms) or in converted (mK)
        self.check_box_T = QtGui.QCheckBox("Plot T", parent=self)
        self.check_box_T.setChecked(True)
        self.check_box_T.stateChanged.connect(self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_T)

        # These are supposed to select whether to autoscale, however they get
        # overruled by a global autoscale setting at the moment
        self.check_box_x = QtGui.QCheckBox("Auto X", parent=self)
        self.check_box_x.setChecked(True)
        self.check_box_x.stateChanged.connect(self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_x)

        self.check_box_y = QtGui.QCheckBox("Auto Y", parent=self)
        self.check_box_y.setChecked(True)
        self.check_box_y.stateChanged.connect(self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_y)

        # push all the widgets to the top of the column, forming a nice layout
        spacer_item = QtGui.QSpacerItem(50, 183, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        self.v_layout.addItem(spacer_item)

        # layout to contain the previous layout on the left, plot on the right
        self.h_layout = QtGui.QHBoxLayout()
        self.h_layout.addLayout(self.v_layout)

        self.mplwidget = MatplotlibZoomWidget(self, usingR=False)
        self.h_layout.addWidget(self.mplwidget)

        self.setLayout(self.h_layout)

        # create convenient aliases for the axes and figure objects
        self.axes = self.mplwidget.axes
        self.figure = self.mplwidget.figure

        # initalize the variable containing the last data point
        self.last_data = 0
        self.setup_axes()

        self.time_values = []
        self.data_values = []
        self.T_values = []

        self.sanitized_list = []

    def setup_axes(self):
        # get the line object from the axes.plot. This way we can update the data
        # used for the line without having to call plot again
        self.line = self.axes.plot(self.get_time(), 1.0, '.-')
        for i in self.line:  # to apply to every Line2dD object, however there should only be one
            i.set_xdata(np.array([]))
            i.set_ydata(np.array([]))

        # formatting and appearance stuff
        # ideally, it would choose nice time units like 30 and 15 minutes
        # but there was some bug with that
        self.axes.tick_params(axis='x', labelsize=8)
        self.axes.tick_params(axis='y', labelsize=8)
        # hfmt = dates.DateFormatter('%m/%d %H:%M')
        hfmt = dates.DateFormatter('%H:%M')
        self.axes.set_xlim([self.get_time() - 1, self.get_time() + 1])
        self.axes.xaxis_date()
        self.axes.xaxis.set_major_formatter(hfmt)
        self.axes.xaxis.set_major_locator(plt.MaxNLocator(7))
        self.axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))

        self.figure.subplots_adjust(bottom=0.1, top=0.96, right=0.98)

    def get_time(self):
        ''' Convenient function to get the time in a usable format '''
        dts = list(map(datetime.datetime.fromtimestamp, [time.time()]))
        return dates.date2num(dts)

    def set_label(self, label_text):
        self.label.setText(label_text)

    def add_point(self, t_stamp, data, T):

        self.display_label.setText("%.3f" % data)
        self.T_label.setText("%.3f" % T)

        print(self.get_time()[0])
        self.time_values.append(t_stamp[0])
        self.data_values.append(data)
        self.T_values.append(T)

        #   line = self.line
        #        if line.get_xdata() == np.array([]):
        #            line.set_xdata(self.get_time())
        #            line.set_ydata(data)
        #        else:
        #            line.set_xdata(np.append(line.get_xdata(), t_stamp))
        #            line.set_ydata(np.append(line.get_ydata(), data))
        #
        self.rescale_and_draw()
        # self.mplwidget.redraw()

    def rescale_and_draw(self):

        [i.set_xdata(self.time_values) for i in self.line]

        if self.check_box_T.isChecked():
            [i.set_ydata(self.T_values) for i in self.line]
        else:
            [i.set_ydata(self.data_values) for i in self.line]

        self.span_x = 0
        # passes in the right arguments to the mplwidget's rescale function
        self.mplwidget.autoscale_axes(scale_x=self.check_box_x.isChecked(),
                                      scale_y=self.check_box_y.isChecked(),
                                      span_x=self.span_x)
        self.mplwidget.redraw()


class FakeInstr(object):
    def __init__(self, *args, **kwargs):
        pass

    def callable(self, *args, **kwargs):
        return 1

    def __getattr__(self, item):
        return self.callable


class FridgeMonitorWindow(QtGui.QMainWindow, ui_fridgemonitor.Ui_FridgeMonitorWindow):
    ''' this program is an interface for our particular dilution fridge setup
    it is set up this way because the Lakeshore 370 uses a multiplexer and requires
    about 10 seconds to get a stable reading on each sensor. So, we have to cycle
    through the 6 resistive thermometers about once per minute. Meanwhile,
    we also read the CMN once per 30 seconds. The CMN can then be used for PID
    control of the heater output of the lakeshore. The PID is poorly tuned right now. '''

    # it may be adaptable for other people's fridges...

    def __init__(self, parent=None):
        super(FridgeMonitorWindow, self).__init__()

        # The UI was created with QT designer.
        self.setupUi(self)

        # a locally defined function that fixes up the UI some more
        self.customize_ui()

        # connect some signals to slots
        self.alarmCheckBox.stateChanged.connect(self.change_alarm)
        self.htrOutputLineEdit.editingFinished.connect(self.set_htr_output)
        self.checkBox_latest.stateChanged.connect(self.set_latest)

        # mutex is a type of lock for threading. No idea if it's used properly
        # or at all here...
        self.mutex = QtCore.QMutex()

        self.parent = parent
        # this is the main thread that takes all the data and emits it as signals
        self.dataThread = fridgemonthread.FridgeMonThread(self.mutex, self)

        self.dataThread.data.connect(self.handle_data)

        # variables for the alarm status
        # some of the values should be moved to a configuration file
        self.ALARM_ON = self.alarmCheckBox.isChecked()
        self.MIN_1K_POT = 1700
        self.MAX_1K_POT = 2000
        self.t_warning = 0
        self.warning1_sent = False
        self.warning2_sent = False
        if DEBUG:
            self.debug = DEBUG
        else:
            self.debug = IOTool.get_debug_setting()
        self.htr_val = 0
        self.htr_range = 0
        self.htr_changed = False

        # information about all the channels is kept in this dictionary
        self.channels = OrderedDict()
        self.chan_dict = {'title': 0, 'subplot': 1}

        self.channels['CMN'] = {'title': 'CMN', 'subplot': 0}
        self.channels['Pirani'] = {'title': 'Pirani', 'subplot': 1}
        # self.channels['LS_1'] = {'title': '1K pot', 'subplot': 0}
        # self.channels['LS_2'] = {'title': 'Still', 'subplot': 1}
        # self.channels['LS_3'] = {'title': 'ICP', 'subplot': 2}
        # self.channels['LS_4'] = {'title': 'MC', 'subplot': 3}
        # self.channels['LS_5'] = {'title': 'Mats', 'subplot': 4}
        # self.channels['LS_9'] = {'title': 'RuO 2k', 'subplot': 5}
        # self.channels['CMN'] = {'title': 'CMN-T', 'subplot': 6}
        # self.channels['CMN-L'] = {'title': 'CMN-L', 'subplot': 7}
        # self.channels['Pirani-1'] = {'title': 'Pirani-1', 'subplot': 8}
        # self.channels['Pirani-2'] = {'title': 'Pirani-2', 'subplot': 9}

        for key in self.channels:
            self.channels[key]['last'] = 0
            self.channels[key]['last_T'] = 0

        # put conversion functions into the dictionary as well. These are
        # used to calculate temperature from resistance
        # self.channels['LS_1']['conversion'] = lambda x: conversions.convert_RX102A(x)
        # self.channels['LS_2']['conversion'] = lambda x: conversions.convert_RX102A(x)
        # self.channels['LS_3']['conversion'] = lambda x: conversions.convert_RX102A(x)
        # self.channels['LS_4']['conversion'] = lambda x: conversions.convert_RX102A(x)
        # self.channels['LS_5']['conversion'] = lambda x: x
        # self.channels['LS_9']['conversion'] = lambda x: conversions.convert_RX202A(x)
        # self.channels['CMN']['conversion'] = lambda x: self.CMN_calculation(x)
        # self.channels['Pirani-1']['conversion'] = lambda x: x
        # self.channels['Pirani-2']['conversion'] = lambda x: x
        self.channels['CMN']['conversion'] = lambda x: self.CMN_calculation(x)
        self.channels['Pirani']['conversion'] = lambda x: x

        # self.channels[8] = ["", 8]
        self.setup_plot()

        # This program also acts as a local server for temperature data and heater commands
        # This happens in a separate thread, the server_thread
        self.data_mutex = QtCore.QMutex()
        self.server_thread = data_server.DataServer(self.data_mutex, self)

        self.server_thread.damping_change.connect(self.update_damping)
        self.server_thread.setpoint_change.connect(self.update_setpoint)
        #self.server_thread.htr_val_change.connect(self.update_htr_val)
        #self.server_thread.htr_range_change.connect(self.update_htr_range)

        self.server_thread.start()

        # keep track of whether the PID control is on
        self.PID_mode = False
        self.PIDLineEdit.setText('0.0')

        ###### PLOT MENU + TOOLBAR SETUP ######

        self.plotToggleControlYAction = QtTools.create_action(self, "Toggle &Left Axes Control",
                                                              slot=self.toggleControlY, shortcut=QKeySequence("Ctrl+L"),
                                                              icon="toggleLeft",
                                                              tip="Toggle whether the mouse adjusts Left axes pan and zoom",
                                                              checkable=True)

        self.plotToggleXControlAction = QtTools.create_action(self, "Toggle &X Axes Control", slot=self.toggleXControl,
                                                              shortcut=QKeySequence("Ctrl+X"),
                                                              icon="toggleX",
                                                              tip="Toggle whether the mouse adjusts x axis pan and zoom",
                                                              checkable=True)

        self.plotAutoScaleXAction = QtTools.create_action(self, "Auto Scale X", slot=self.toggleAutoScaleX,
                                                          shortcut=QKeySequence("Ctrl+A"),
                                                          icon="toggleAutoScaleX", tip="Turn autoscale X on or off",
                                                          checkable=True)

        self.plotAutoScaleYAction = QtTools.create_action(self, "Auto Scale Y", slot=self.toggleAutoScaleY,
                                                          shortcut=QKeySequence("Ctrl+D"),
                                                          icon="toggleAutoScaleL",
                                                          tip="Turn autoscale Left Y on or off", checkable=True)

        self.plotDragZoomAction = QtTools.create_action(self, "Drag to zoom", slot=self.toggleDragZoom,
                                                        shortcut=QKeySequence("Ctrl+Z"),
                                                        icon="zoom", tip="Turn drag to zoom on or off", checkable=True)

        self.plotPanAction = QtTools.create_action(self, "Drag to Pan", slot=self.togglePan,
                                                   shortcut=QKeySequence("Ctrl+P"),
                                                   icon="pan", tip="Turn drag to Pan on or off", checkable=True)

        self.changeYscale = QtTools.create_action(self, "Set Y log", slot=self.setYscale, shortcut=None,
                                                  icon="logY", tip="Set the y scale to log")

        #      self.clearPlot = QtTools.create_action(self,"Clear Plot", slot=self.clear_plot, shortcut=None,
        #                                     icon="clear", tip="Clears the data arrays")

        self.plotToolbar = self.addToolBar("Plot")
        self.plotToolbar.setObjectName("PlotToolBar")

        self.plotToolbar.addAction(self.plotToggleXControlAction)
        self.plotToolbar.addAction(self.plotToggleControlYAction)

        self.plotToolbar.addAction(self.plotAutoScaleXAction)
        self.plotToolbar.addAction(self.plotAutoScaleYAction)

        self.plotToolbar.addAction(self.plotPanAction)
        self.plotToolbar.addAction(self.plotDragZoomAction)

        self.plotToolbar.addAction(self.changeYscale)

        # interface = IOTool.get_interface_setting()
        # print ("We will be using: " + interface)
        # DONE: MAKE THIS DYNAMIC
        #        self.heater = YOKOGS200.Instrument ('GPIB0::19', self.debug)
        #        self.CMN = HP4263B.Instrument('GPIB0::17', debug=self.debug)
        #        self.pirani = MKS146C.Instrument("COM8", self.debug)
        self.set_devices()
        self.sanitized_list = []

        self.update_heater_display()

        self.setpoint = 0
        self.integral = 0
        self.derivative = 0

        # PID constants
        self.K_p = 1
        self.K_i = 0

        # set clicked handlers (btn.clicked.connect(fnct) instead of @pyqtSignature("") w/ fnct = on_btn_clicked
        for i in ['startStopButton', 'autoScaleButton', 'manualScaleButton', 'cancelButton', 'updateButton',
                  'updatePIDButton', 'radioButton_PID', 'radioButton_Man']:
            try:  # make sure everythings disconnected before
                getattr(self, i).clicked.disconnect()
            except:
                pass
        self.startStopButton.clicked.connect(self.on_startStopButton_clicked)
        self.autoScaleButton.clicked.connect(self.on_autoScaleButton_clicked)
        self.manualScaleButton.clicked.connect(self.on_manualScaleButton_clicked)
        self.cancelButton.clicked.connect(self.on_cancelButton_clicked)
        self.updateButton.clicked.connect(self.on_updateButton_clicked)
        self.updatePIDButton.clicked.connect(self.on_updatePIDButton_clicked)
        self.radioButton_PID.clicked.connect(self.on_radioButton_PID_clicked)
        self.radioButton_Man.clicked.connect(self.on_radioButton_Man_clicked)

    def customize_ui(self):

        widget_ID = 0
        self.plot_widgets = []
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)

        for i in range(2):
            for j in range(5):
                new_widget = MiniPlot(self.plot_holder)
                self.grid.addWidget(new_widget, j, i)
                self.plot_widgets.append(new_widget)
                widget_ID = widget_ID + 1
                new_widget.mplwidget.limits_changed.connect(self.when_scale_changed)
        self.plot_holder.setLayout(self.grid)

    def setup_plot(self):
        # self.mplwidget.figure.clear()

        for idx in self.channels:
            chan = self.channels[idx]

            widget = self.plot_widgets[chan['subplot']]
            widget.set_label(chan['title'])

        # fig = widget.figure

        # fig.clear()
        # chan['axes'] = fig.add_subplot(1,1,1)
        # widget.axes =

    #            chan['axes'] = widget.axes
    #            chan['axes'].lines = []
    #            chan['line'], = chan['axes'].plot(self.get_time(),0, 'o-')
    #            chan['line'].set_xdata(np.array([]))
    #            chan['line'].set_ydata(np.array([]))

    def CMN_calculation(self, raw_value):
        mH = raw_value * 1000
        try:
            equation = str(self.equationLineEdit.text())
            return eval(equation)
        except:
            # in case of problem, report 0 Kelvin :P
            return 0

    def T_for_PID(self, T_CMN, T_RuO):
        # temperatures in mK

        T_low = 100.
        T_high = 250.

        if T_RuO == 0:
            return T_CMN
        elif T_CMN < T_low:
            return T_CMN
        elif T_CMN < T_high:
            frac = (T_CMN - T_low) / (T_high - T_low)

            return frac * T_RuO + (1 - frac) * T_CMN

        else:
            return T_RuO

    def get_time(self):
        dts = list(map(datetime.datetime.fromtimestamp, [time.time()]))
        return dates.date2num(dts)
    def update_damping(self, damping_factor):
        logging.info(("Damping changed to: ", damping_factor))

        self.damping_factor = float(damping_factor)
        self.dampingLineEdit.setText(str(damping_factor))
    def handle_data(self, name_and_data):
        try:
            self.data_mutex.lock()
            name, data = name_and_data

            self.data_string = self.data_string + "     " + str(data)

            T = self.channels[name]['conversion'](data)

            logging.debug((name, data))

            self.channels[name]['last'] = data
            self.channels[name]['last_T'] = T

            self.plot_widgets[self.channels[name]['subplot']].add_point(self.get_time(), data, T)

            if name == 'CMN':
                # convert CMN to mK and write it to the file as well
                # data = self.CMN_calc(data)
                # CMN_temp = T

                # calculate PID_temp in mK
                PID_temp = T  # self.T_for_PID(T, self.channels['LS_4']['last_T'] * 1000)
                logging.info("PID interpolated temperature: " + str(PID_temp) + " setpoint: " + str(self.setpoint))

                self.data_string = self.data_string + "     " + str(PID_temp)

                if self.PID_mode:
                    # make sure the heater range is correct for PID!

                    delta = (self.setpoint - PID_temp)
                    proportional_htr = self.K_p * delta
                    logging.debug(("proportional: ", delta, 'heater: ', proportional_htr))

                    dt = time.time() - self.last_time

                    self.integral = max(0, self.integral + delta * dt)
                    integral_htr = self.K_i * self.integral
                    logging.debug(("Integral: ", self.integral, 'heater: ', integral_htr))

                    self.derivative = min(0, self.derivative + (self.setpoint - PID_temp))

                    # convert the old lakeshore percent setting to a current by dividing by 100 and multiplying by 3.16 mA
                    new_output = min(100.0, max(0.0, proportional_htr + integral_htr)) * 0.01 * 3.16

                    # safety mechanism for PID outrange
                    if PID_temp > 450:
                        self.update_setpoint(0)
                        output = 0
                    else:
                        output = (self.damping_factor * self.old_output + new_output) / (self.damping_factor + 1)

                    self.old_output = output
                    logging.info("Calcultated Output: " + str(new_output) + ' mA')
                    logging.info("Damped Output: " + str(output) + ' mA')
                    self.heater.set_current(output * 1e-3)

                # get heater setting and include it in the data line                                                                                                                                                                                                                                                         date textbox
                heater_output = self.heater.measure()
                self.data_string = self.data_string + "     " + str(heater_output)

                # update only if user isn't currently trying to enter a value
                if not self.htr_changed:
                    self.htrOutputLineEdit.setText(str(heater_output))

                self.data_string = "%.1f" % (time.time()) + '    '
                self.data_string += '    '.join([str(self.channels[x]['last']) for x in self.channels])

                self.output_file.write(self.data_string + '\n')

                self.plot_widgets[self.channels[name]['subplot']].add_point(self.get_time(), data, T)

            if name == 'LS_1' and self.ALARM_ON:
                self.check_alarm(data)

            self.data_mutex.unlock()
        except:
            logging.error(("Unable to handle data:", name_and_data))
            if DEBUG:
                logging.error(sys.exc_info())

    def autoscale_axes(self, axes):

        x_max = -np.inf
        x_min = np.inf

        y_max = -np.inf
        y_min = np.inf

        for line in axes.get_lines():
            xdata = line.get_xdata()

            x_max = max(x_max, np.amax(xdata))
            x_min = min(x_min, np.amin(xdata))

            ydata = line.get_ydata()

            y_max = max(y_max, np.amax(ydata))
            y_min = min(y_min, np.amin(ydata))

        self.history_length = 0

        if x_max == x_min:
            x_min = x_max - 1

        if y_max == y_min:
            y_min = 0
            y_max = y_max * 2

        if self.history_length == 0:
            axes.set_xlim(x_min, x_max)
        else:
            axes.set_xlim(x_max - self.history_length, x_max)

        axes.set_ylim(y_min, y_max)

    def when_scale_changed(self, a, lims):
        if self.checkBox_lock_x.isChecked():
            for pw in self.plot_widgets:
                pw.axes.set_xlim(lims[0])
                pw.rescale_and_draw()

    def change_alarm(self):
        self.ALARM_ON = self.alarmCheckBox.isChecked()
        logging.debug(self.ALARM_ON)

    def set_htr_range(self):
        self.htr_range = self.htrRangeComboBox.currentIndex()
        self.htr_changed = True

    def set_latest(self):
        self.show_latest = self.checkBox_latest.isChecked()

    def set_htr_output(self):
        try:
            val = float(self.htrOutputLineEdit.text())
            if val < 0:
                self.htrOutputLineEdit.setText("0.0")
                val = 0
            if val > 100:
                self.htrOutputLineEdit.setText("100.0")
                val = 100.0
            self.htr_val = val
        except ValueError:
            self.htrOutputLineEdit.setText(str(self.htr_val))

    #    def CMN_calc(self,raw_value):
    #        return -4.36894/(-raw_value*1000+2.93629)

    def check_alarm(self, temp):
        t_current = time.time()
        if temp > self.MAX_1K_POT and self.warning1_sent == False:
            self.msg['BODY'] = "1K pot is too cold: %.3f" % temp

            textmsg.send_txt(self.msg)
            self.warning1_sent = True
            self.t_warning = t_current
        elif temp < self.MIN_1K_POT and self.warning2_sent == False:
            self.msg['BODY'] = "1K pot is too warm: %.3f" % temp
            logging.info(self.msg)
            textmsg.send_txt(self.msg)
            self.warning2_sent = True
            self.t_warning = t_current
        elif t_current - self.t_warning > 900:  # resend warning up to every 15 minutes
            self.warning1_sent = False
            self.warning2_sent = False

            # @pyqtSignature("")

    def on_startStopButton_clicked(self):
        if self.dataThread.isStopped() and self.startStopButton.text() == 'Start':
            if not self.ready_start():
                logging.error("Unable to start")
                msgbox = QtGui.QErrorMessage(self)
                msgbox.setWindowTitle("Error Connecting")
                msgbox.showMessage("Unable to start Fridge Monitor. Make sure all your devices are connected.")
                return
            self.t_start = time.time()
            self.last_time = time.time()

            #            self.pirani = MKS146C.Instrument('COM8', debug = True) #'/dev/ttyUSB0'

            self.data_string = "%.1f" % (time.time())
            output_file_name = IOTool.open_therm_file()
            logging.info("Will save data to: " + output_file_name)

            self.old_output = self.heater.measure()
            self.output_file = open(output_file_name, 'w')

            self.dataThread.initialize(None, self.CMN, self.pirani, self.debug)
            self.dataThread.start()

            self.startStopButton.setText("Stop")
        elif self.startStopButton.text() == "Stop":
            self.dataThread.stop()

            self.pirani.close()
            self.output_file.close()

            self.startStopButton.setText("Start")
        else:
            logging.warning(("Should not have reached here:", self.dataThread.isStopped(), self.startStopButton.text()))

    # @pyqtSignature("")
    def on_autoScaleButton_clicked(self):
        for pw in self.plot_widgets:
            pw.check_box_x.setChecked(True)
            pw.check_box_y.setChecked(True)
            pw.rescale_and_draw()

        logging.debug("Auto scale requested!")

    # @pyqtSignature("")
    def on_manualScaleButton_clicked(self):
        for pw in self.plot_widgets:
            pw.check_box_x.setChecked(False)
            pw.check_box_y.setChecked(False)
            pw.rescale_and_draw()

        logging.debug("Manual scale requested!")

    def set_htr_output(self):
        self.htrOutputLineEdit.setStyleSheet("color: rgb(255, 0, 0);")
        self.htr_changed = True


    def update_htr_val(self, val):
        logging.error(("Should not have reached here: ", val))
    #def update_htr_val(self, val):
    #    """triggered by a signal from the FridgeServer"""
    #    logging.debug("lakeshore update val", val)
    #    self.htrOutputLineEdit.setText(str(val))
    #    self.lakeshore.set_heater_range(float(val))
    #    self.on_updateButton_clicked()

    # @pyqtSignature("")
    def on_updateButton_clicked(self):
        self.htrOutputLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.htrRangeComboBox.setStyleSheet("color: rgb(0, 0, 0);")
        # set the heater range and current
        try:
            val = float(self.htrOutputLineEdit.text())

            if val < 0 or val > 100:
                self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))
            else:
                logging.debug("setting to " + str(val))
                self.heater.set_current (val * 1e-3)
        except ValueError:
            self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))


        self.htr_changed = False

    # @pyqtSignature("")
    def on_cancelButton_clicked(self):
        self.update_heater_display()

    def update_heater_display(self):
        # retrieve actual settings from instrument to fill box
        self.htr_changed = False
        self.htrOutputLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.htrRangeComboBox.setStyleSheet("color: rgb(0, 0, 0);")
        self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))

    # @pyqtSignature("")
    def on_radioButton_PID_clicked(self):
        logging.debug("in PID mode")
        # RESET THE INTEGRAL BECAUSE PID TEMPERATURE LIKELY CHANGED!
        self.integral = 0
        self.derivative = 0
        self.PID_mode = True

    # @pyqtSignature("")
    def on_radioButton_Man_clicked(self):
        logging.debug("In manual mode")
        self.PID_mode = False

        # @pyqtSignature("")

    def on_updatePIDButton_clicked(self):
        self.update_setpoint(float(self.PIDLineEdit.text()))

    def update_setpoint(self, new_setpoint):
        logging.debug(new_setpoint)
        new_setpoint = float(new_setpoint)
        if new_setpoint < 510 and new_setpoint >= 0:
            self.setpoint = float(new_setpoint)
            # self.integral = 0
            # seff.derivative = 0

        self.PIDLineEdit.setText(str(self.setpoint))
        self.K_p = float(self.proportionalLineEdit.text())
        self.K_i = float(self.integralLineEdit.text())
        logging.debug((self.K_p, self.K_i))

    # change the x axis scale to linear if it was log and reverse
    def set_Xaxis_scale(self, axis):
        curscale = axis.get_xscale()
        #        print curscale
        if curscale == 'log':
            axis.set_xscale('linear')
        elif curscale == 'linear':
            axis.set_xscale('log')

    # change the y axis scale to linear if it was log and reverse
    def set_Yaxis_scale(self, axis):
        curscale = axis.get_yscale()
        #        print curscale
        if curscale == 'log':
            axis.set_yscale('linear')
        elif curscale == 'linear':
            axis.set_yscale('log')

    def setXscale(self):
        self.set_Xaxis_scale(self.ax)

    def setYscale(self):
        self.set_Yaxis_scale(self.ax)

    def toggleAutoScaleX(self):
        if self.plotAutoScaleXAction.isChecked():
            self.plotToggleXControlAction.setChecked(False)
        else:
            self.plotToggleXControlAction.setChecked(True)
        self.updateZoomSettings()

    def toggleAutoScaleY(self):
        if self.plotAutoScaleYAction.isChecked():
            self.plotToggleControlYAction.setChecked(False)
        else:
            self.plotToggleControlYAction.setChecked(True)
        self.updateZoomSettings()

    def toggleXControl(self):
        if self.plotToggleXControlAction.isChecked():
            self.plotAutoScaleXAction.setChecked(False)
        self.updateZoomSettings()

    def toggleControlY(self):
        if self.plotToggleControlYAction.isChecked():
            self.plotAutoScaleYAction.setChecked(False)
        self.updateZoomSettings()

    def togglePan(self):
        if self.plotDragZoomAction.isChecked():
            self.plotDragZoomAction.setChecked(False)
        self.updateZoomSettings()

    def toggleDragZoom(self):
        if self.plotPanAction.isChecked():
            self.plotPanAction.setChecked(False)
        self.updateZoomSettings()

    def updateZoomSettings(self):
        for widget in self.plot_widgets:
            mplwidget = widget.mplwidget

            mplwidget.setActiveAxes(self.plotToggleXControlAction.isChecked(),
                                    self.plotToggleControlYAction.isChecked())
            if self.plotDragZoomAction.isChecked():
                mplwidget.mouseMode = mplwidget.ZOOM_MODE
            elif self.plotPanAction.isChecked():
                mplwidget.mouseMode = mplwidget.PAN_MODE

            mplwidget.set_autoscale_x(self.plotAutoScaleXAction.isChecked())
            mplwidget.set_autoscale_y(self.plotAutoScaleYAction.isChecked())

    def set_devices(self):
        self.heater = FakeInstr()  # LS370_janis.Instrument('name', debug=True)
        self.CMN = FakeInstr()  # HP4263B.Instrument('name', debug=True)
        self.pirani = FakeInstr()  # MKS146C.Instrument('name', debug=True)

    def refresh_devices(self):
        if self.parent is not None:
            instrument_list = self.parent.instr_hub.get_instrument_list()
            # print(self.instrument_list)

            # print(self.parentClass.instr_hub.get_port_param_pairs())
            # print(self.parentClass.instr_hub.get_instrument_nb())

            z = instrument_list.items()

            ports = list()
            instruments = list()
            names = list()
            for x, y in z:
                if x is not None and "ComputerTime" not in x:
                    ports.append(x)
                    instruments.append(instrument_list[x])
                    names.append(instrument_list[x].ID_name)
                    # print(x,self.instrument_list[x].ID_name)
            self.sanitized_list = list(zip(names, ports, instruments))

            return

    def ready_start(self):
        try:
            if self.parent is not None:
                self.parent.stop_DTT()
                self.refresh_devices()
                self.heater = self.CMN = self.pirani = None
                for instr in self.sanitized_list:  # find required devices
                    if self.heater is None or CHOOSE_FIRST_DEVICE:
                        if instr[0] in HEATER_ALLOWED:
                            self.heater = instr[2]

                    if self.CMN is None or CHOOSE_FIRST_DEVICE:
                        if instr[0] in CMN_ALLOWED:
                            self.CMN = instr[2]

                    if self.pirani is None or CHOOSE_FIRST_DEVICE:
                        if instr[0] in PIRANI_ALLOWED:
                            self.pirani = instr[2]
                # CHECK IF WE HAVE REQUIRED DEVICES
                flag = True
                if self.heater is None:
                    if DEBUG:
                        self.heater = FakeInstr()  # YOKOGS200.Instrument ('GPIB0::19', debug = True)
                    else:
                        logging.info("Missing heater device.")
                        flag = False
                if self.CMN is None:
                    if DEBUG:
                        self.CMN = FakeInstr()  # HP4263B.Instrument('name', debug=True)
                    else:
                        logging.info("Missing CMN device.")
                        flag = False
                if self.pirani is None:
                    if DEBUG:
                        self.pirani = FakeInstr()  # MKS146C.Instrument('name', debug=True)
                    else:
                        logging.info("Missing Pirani device.")
                        flag = False
                return flag  # false if missing a device
            else:
                return False
        except:
            logging.error("Unable to ready_start")
            if DEBUG:
                logging.error(sys.exc_info())
            return False


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain

    create a QDock widget and store a reference to the widget
    """

    mywidget = FridgeMonitorWindow(parent=parent)
    # create a QDockWidget
    FM_NOLS_DockWidget = QtGui.QDockWidget("Fridge Monitor (No LS)", parent)
    FM_NOLS_DockWidget.setObjectName("FridgeMonitorWidget_NOLS")
    FM_NOLS_DockWidget.setAllowedAreas(
        QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

    # fill the dictionnary with the widgets added into LabGuiMain
    parent.widgets['FridgeMonitorWidget_NOLS'] = mywidget

    FM_NOLS_DockWidget.setWidget(mywidget)
    parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, FM_NOLS_DockWidget)

    # Enable the toggle view action
    parent.windowMenu.addAction(FM_NOLS_DockWidget.toggleViewAction())
    FM_NOLS_DockWidget.hide()


if __name__ == "__main__":
    pass


