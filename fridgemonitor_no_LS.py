
# Changes to make:
# add print function
# Add conversion to temperature
# Add helium level meter support
# add pressure gauge reading


from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from fridgemonitor_parts import data_server, textmsg, ui_fridgemonitor
from fridgemonitor_parts import fridgemonthread
from fridgemonitor_parts import conversions

import fridgemonitor_parts.chart_recorder as cr

from LabDrivers import HP4263B
from LabDrivers import MKS146C
from LabDrivers import YOKOGS200

from LabTools.IO import IOTool
import time, datetime

from LabTools.Display.mplZoomWidget import MatplotlibZoomWidget
from LabTools.Display import QtTools


import numpy as np
from matplotlib import dates
from matplotlib import ticker
import matplotlib.pyplot as plt


#TODO:
    #new file each day
    #set history length
    # show pressure
    # show He and N2 levels
    # different colours :)

class MiniPlot(QFrame):
    # This class is for each of the panels in the fridgemonitor
    # It includes the main plot and a few checkboxes to change settings

    def __init__(self, label_text = 'Therm', parent = None):
        super(MiniPlot, self).__init__()  
        
        # style sheet is used to make the darker grey background
        self.setStyleSheet("background-color: rgb(190,190,190); ")

        # this is the lefthand part with the numerical display and the checkboxes
        self.v_layout = QVBoxLayout()

        # The name of the thermometer/sensor goes here
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Arial", 12))
        self.v_layout.addWidget(self.label)
 
        # the raw value (ohms etc.) goes here
        self.display_label = QLabel("", )
        self.display_label.setAlignment(Qt.AlignHCenter)
        self.display_label.setFont(QFont("Arial", 12))
        self.display_label.setStyleSheet("background-color: rgb(250,190,190); ")
        self.v_layout.addWidget(self.display_label)
        
        # the converted temperature value goes here
        self.T_label = QLabel("", )
        self.T_label.setAlignment(Qt.AlignHCenter)
        self.T_label.setFont(QFont("Arial", 12))
        self.T_label.setStyleSheet("background-color: rgb(250,190,190); ")
        self.v_layout.addWidget(self.T_label)

        # whether to plot in raw (ohms) or in converted (mK)
        self.check_box_T = QCheckBox("Plot T", parent = self)
        self.check_box_T.setChecked(True)
        self.connect (self.check_box_T, SIGNAL("stateChanged(int)"), self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_T)
       
        
        # These are supposed to select whether to autoscale, however they get 
        # overruled by a global autoscale setting at the moment
        self.check_box_x = QCheckBox("Auto X", parent = self)
        self.check_box_x.setChecked(True)
        self.connect (self.check_box_x, SIGNAL("stateChanged(int)"), self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_x)
       
        self.check_box_y = QCheckBox("Auto Y", parent = self)
        self.check_box_y.setChecked(True)
        self.connect (self.check_box_y, SIGNAL("stateChanged(int)"), self.rescale_and_draw)
        self.v_layout.addWidget(self.check_box_y)
        
        # push all the widgets to the top of the column, forming a nice layout
        spacer_item = QSpacerItem(50, 183, QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.v_layout.addItem(spacer_item)
        
        # layout to contain the previous layout on the left, plot on the right
        self.h_layout = QHBoxLayout()
        self.h_layout.addLayout(self.v_layout)
        
        self.mplwidget = MatplotlibZoomWidget(self, usingR = False)
        self.h_layout.addWidget(self.mplwidget)    
        
        self.setLayout (self.h_layout)
        
        # create convenient aliases for the axes and figure objects
        self.axes = self.mplwidget.axes
        self.figure = self.mplwidget.figure
        
        #initalize the variable containing the last data point
        self.last_data = 0
        self.setup_axes()


        self.time_values = []
        self.data_values = []
        self.T_values = []

        
    def setup_axes(self):
        #get the line object from the axes.plot. This way we can update the data
        # used for the line without having to call plot again
        self.line, = self.axes.plot(self.get_time(), 1.0, '.-')
        self.line.set_xdata(np.array([]))
        self.line.set_ydata(np.array([]))
        
        # formatting and appearance stuff
        # ideally, it would choose nice time units like 30 and 15 minutes
        # but there was some bug with that
        self.axes.tick_params(axis='x', labelsize=8)
        self.axes.tick_params(axis='y', labelsize=8)  
        #hfmt = dates.DateFormatter('%m/%d %H:%M') 
        hfmt = dates.DateFormatter('%H:%M') 
        self.axes.set_xlim([self.get_time() - 1, self.get_time() + 1])
        self.axes.xaxis_date()
        self.axes.xaxis.set_major_formatter(hfmt)
        self.axes.xaxis.set_major_locator(plt.MaxNLocator(7))
        self.axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset = False))
        
        self.figure.subplots_adjust (bottom = 0.1, top = 0.96, right = 0.98) 
        
        

        
    def get_time(self):
        # Convenient function to get the time in a usable format
        dts = map(datetime.datetime.fromtimestamp, [time.time()])
        return dates.date2num(dts)
            
    def set_label(self, label_text):
        self.label.setText(label_text)
    
    def add_point(self, t_stamp, data, T):
        
        self.display_label.setText("%.3f"%data)
        self.T_label.setText("%.3f"%T)
        
        print(self.get_time()[0])
        self.time_values.append(t_stamp[0])
        self.data_values.append(data)
        self.T_values.append (T)

          
     #   line = self.line  
#        if line.get_xdata() == np.array([]):
#            line.set_xdata(self.get_time())
#            line.set_ydata(data)        
#        else:
#            line.set_xdata(np.append(line.get_xdata(), t_stamp))
#            line.set_ydata(np.append(line.get_ydata(), data))
#            
        self.rescale_and_draw()
        #self.mplwidget.redraw()
        
    def rescale_and_draw(self):
        
        self.line.set_xdata(self.time_values)
        
        if self.check_box_T.isChecked():
            self.line.set_ydata(self.T_values)
        else:
            self.line.set_ydata(self.data_values)
            
        self.span_x = 0
        # passes in the right arguments to the mplwidget's rescale function
        self.mplwidget.autoscale_axes(scale_x = self.check_box_x.isChecked(), 
                                      scale_y = self.check_box_y.isChecked(), 
                                        span_x = self.span_x)
        self.mplwidget.redraw()
            
            
class FridgeMonitorWindow(QMainWindow, ui_fridgemonitor.Ui_FridgeMonitorWindow):
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
        self.connect (self.htrOutputLineEdit, SIGNAL ("editingFinished()"), self.set_htr_output)
        
        self.connect (self.checkBox_latest, SIGNAL("stateChanged(int)"), self.set_latest)

        # mutex is a type of lock for threading. No idea if it's used properly
        # or at all here...
        self.mutex = QMutex()         

        # this is the main thread that takes all the data and emits it as signals
        self.dataThread = fridgemonthread.FridgeMonThread(self.mutex, self)  
        self.connect(self.dataThread, SIGNAL("data(PyQt_PyObject)"),
                     self.handle_data)

        # variables for the alarm status
        # some of the values should be moved to a configuration file
        self.ALARM_ON = self.alarmCheckBox.isChecked()
        self.MIN_1K_POT = 1700
        self.MAX_1K_POT = 2000
        self.t_warning = 0
        self.warning1_sent=False
        self.warning2_sent=False
        
        self.debug = IOTool.get_debug_setting()

        self.htr_val = 0
        self.htr_range = 0
        self.htr_changed = False

        
        # information about all the channels is kept in this dictionary        
        self.channels = {}
        self.chan_dict = {'title': 0, 'subplot': 1}
        
        self.channels['CMN'] = {'title':'CMN', 'subplot':0}
        self.channels['Pirani'] = {'title':'Pirani', 'subplot':1}
        
        for key in self.channels:
            self.channels[key]['last'] = 0
            self.channels[key]['last_T'] = 0
        # put conversion functions into the dictionary as well. These are 
        # used to calculate temperature from resistance

        self.channels['CMN']['conversion'] = lambda x: self.CMN_calculation(x)
        self.channels['Pirani']['conversion'] = lambda x: x
        
        
        #self.channels[8] = ["", 8]
        self.setup_plot()
        
        
        # This program also acts as a local server for temperature data and heater commands
        # This happens in a separate thread, the server_thread
        self.data_mutex = QMutex()
        self.server_thread = data_server.DataServer(self.data_mutex, self)
        self.server_thread.start()
        
        self.connect(self.server_thread, SIGNAL("setpoint_change(PyQt_PyObject)"),
                     self.update_setpoint)
                     
        self.connect(self.server_thread, SIGNAL("damping_change(PyQt_PyObject)"),
                     self.update_damping)        
                     
        # keep track of whether the PID control is on
        self.PID_mode = False
        self.PIDLineEdit.setText('0.0')
        
###### PLOT MENU + TOOLBAR SETUP ######          
               
        self.plotToggleControlYAction = QtTools.create_action(self,"Toggle &Left Axes Control", slot=self.toggleControlY, shortcut=QKeySequence("Ctrl+L"),
                                        icon="toggleLeft", tip="Toggle whether the mouse adjusts Left axes pan and zoom", checkable=True)                   

        self.plotToggleXControlAction = QtTools.create_action(self,"Toggle &X Axes Control", slot=self.toggleXControl, shortcut=QKeySequence("Ctrl+X"),
                                        icon="toggleX", tip="Toggle whether the mouse adjusts x axis pan and zoom", checkable=True)                   
                    
        self.plotAutoScaleXAction = QtTools.create_action(self,"Auto Scale X", slot=self.toggleAutoScaleX, shortcut=QKeySequence("Ctrl+A"),
                                        icon="toggleAutoScaleX", tip="Turn autoscale X on or off", checkable=True)                   
                    
        self.plotAutoScaleYAction = QtTools.create_action(self,"Auto Scale Y", slot=self.toggleAutoScaleY, shortcut=QKeySequence("Ctrl+D"),
                                        icon="toggleAutoScaleL", tip="Turn autoscale Left Y on or off", checkable=True)                   

                
        self.plotDragZoomAction = QtTools.create_action(self,"Drag to zoom", slot=self.toggleDragZoom, shortcut=QKeySequence("Ctrl+Z"),
                                        icon="zoom", tip="Turn drag to zoom on or off", checkable=True)                   

        self.plotPanAction = QtTools.create_action(self,"Drag to Pan", slot=self.togglePan, shortcut=QKeySequence("Ctrl+P"),
                                        icon="pan", tip="Turn drag to Pan on or off", checkable=True)                   
         
        self.changeYscale=QtTools.create_action(self,"Set Y log", slot=self.setYscale, shortcut=None,
                                        icon="logY", tip="Set the y scale to log")
                                        
  #      self.clearPlot = QtTools.create_action(self,"Clear Plot", slot=self.clear_plot, shortcut=None,
   #                                     icon="clear", tip="Clears the data arrays")                       

        self.plotToolbar = self.addToolBar("Plot")
        self.plotToolbar.setObjectName ( "PlotToolBar")
        
        self.plotToolbar.addAction(self.plotToggleXControlAction)
        self.plotToolbar.addAction(self.plotToggleControlYAction)

        self.plotToolbar.addAction(self.plotAutoScaleXAction)
        self.plotToolbar.addAction(self.plotAutoScaleYAction)
 
        self.plotToolbar.addAction(self.plotPanAction)
        self.plotToolbar.addAction(self.plotDragZoomAction)   

        self.plotToolbar.addAction(self.changeYscale)

        self.CMN = HP4263B.Instrument('GPIB0::17', self.debug)
        self.heater = YOKOGS200.Instrument ('GPIB0::19', self.debug)
        self.pirani = MKS146C.Instrument("COM8", self.debug) 
        
        self.update_heater_display()            
        
        self.setpoint = 0
        self.integral = 0
        self.derivative = 0
        
        # PID constants
        self.K_p = 1
        self.K_i = 0
        
    def customize_ui(self):

        widget_ID = 0
        self.plot_widgets = []
        self.grid = QGridLayout()  
        self.grid.setSpacing(5)
        
        for i in range(1):
            for j in range (2):
                new_widget = MiniPlot(self.plot_holder)
                self.grid.addWidget(new_widget, j,i)
                self.plot_widgets.append(new_widget)               
                widget_ID = widget_ID + 1
                self.connect(new_widget.mplwidget, SIGNAL("limits_changed(int,PyQt_PyObject)"), self.when_scale_changed)
        self.plot_holder.setLayout(self.grid)
        
    def setup_plot(self):
       # self.mplwidget.figure.clear()

        for idx in self.channels:

            chan = self.channels[idx]

            widget = self.plot_widgets[chan['subplot']]
            widget.set_label (chan['title'])
                       
           # fig = widget.figure
            

            #fig.clear()
            #chan['axes'] = fig.add_subplot(1,1,1)
            #widget.axes = 
#            chan['axes'] = widget.axes
#            chan['axes'].lines = []
#            chan['line'], = chan['axes'].plot(self.get_time(),0, 'o-')
#            chan['line'].set_xdata(np.array([]))
#            chan['line'].set_ydata(np.array([]))           
            
    def CMN_calculation (self, raw_value):
        mH = raw_value * 1000
        equation = str(self.equationLineEdit.text())
        return eval(equation)
    
    def T_for_PID (self,T_CMN, T_RuO):
        # temperatures in mK
    
        T_low = 100.
        T_high = 250.
        
        if T_RuO == 0:
            return T_CMN            
        elif T_CMN < T_low:
            return T_CMN
        elif T_CMN < T_high:
            frac = (T_CMN - T_low)/(T_high - T_low)       
            
            return frac * T_RuO + (1-frac) * T_CMN
            
        else:
            return T_RuO
    

    def get_time(self):
        dts = map(datetime.datetime.fromtimestamp, [time.time()])
        return dates.date2num(dts)
        
    def handle_data(self, name_and_data):
        self.data_mutex.lock()
        name,data = name_and_data
        
        self.data_string = self.data_string + "     " + str(data)
        
        T = self.channels[name]['conversion'](data)
        
        if name == 'CMN':
            #convert CMN to mK and write it to the file as well
            #data = self.CMN_calc(data)
            #CMN_temp = T
        
            # calculate PID_temp in mK
            PID_temp = T#self.T_for_PID(T, self.channels['LS_4']['last_T'] * 1000)
            print "PID interpolated temperature: " + str(PID_temp) + " setpoint: " + str(self.setpoint)
            
            self.data_string = self.data_string + "     " + str(PID_temp)

            if self.PID_mode:
                # make sure the heater range is correct for PID!          
                
                delta = (self.setpoint - PID_temp)
                proportional_htr = self.K_p * delta
                print "proportional: ", delta, 'heater: ', proportional_htr 
                
                dt = time.time() - self.last_time
                             
                self.integral = max (0, self.integral + delta * dt)
                integral_htr =  self.K_i * self.integral
                print "Integral: ",  self.integral, 'heater: ', integral_htr
                
                self.derivative = min (0, self.derivative + (self.setpoint - PID_temp))
                
                #convert the old lakeshore percent setting to a current by dividing by 100 and multiplying by 3.16 mA
                new_output = min (100.0, max(0.0, proportional_htr + integral_htr)) * 0.01 * 3.16
                
                #safety mechanism for PID outrange
                if PID_temp > 450: 
                    self.update_setpoint(0)
                    output = 0
                else:
                    output = (self.damping_factor * self.old_output + new_output)/(self.damping_factor + 1)
                
                self.old_output = output
                print "Calcultated Output: " + str(new_output) + ' mA'
                print "Damped Output: " + str(output) + ' mA'
                self.heater.set_current(output * 1e-3)

            #get heater setting and include it in the data line                                                                                                                                                                                                                                                         date textbox
            heater_output = self.heater.measure()
            self.data_string = self.data_string + "     " + str(heater_output)
            
            #update only if user isn't currently trying to enter a value
            if not self.htr_changed:
                self.htrOutputLineEdit.setText(str(heater_output))
             
                
            self.output_file.write(self.data_string + '\n')
            self.data_string = "%.1f"%(time.time())
            self.last_time  = time.time()
        print name, data
        
        self.channels[name]['last'] = data
        self.channels[name]['last_T'] = T
        
        self.plot_widgets[self.channels[name]['subplot']].add_point(self.get_time(), data, T)  
        
        if name == 'LS_1' and self.ALARM_ON:

            self.check_alarm(data)     
            
        self.data_mutex.unlock()         
        
    def autoscale_axes(self, axes):
        
        x_max = -np.inf
        x_min = np.inf
 
        y_max = -np.inf
        y_min = np.inf
        
        for line in axes.get_lines():
            xdata = line.get_xdata()
           
            x_max = max (x_max, np.amax(xdata))
            x_min = min (x_min, np.amin(xdata))

            ydata = line.get_ydata()
            
            y_max = max (y_max, np.amax(ydata))
            y_min = min (y_min, np.amin(ydata))
            
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
                pw.axes.set_xlim (lims[0])
                pw.rescale_and_draw()
            
    def set_latest(self):
        self.show_latest = self.checkBox_latest.isChecked()
        
    def set_htr_output(self):
        try:
            val = float(self.htrOutputLineEdit.text())
            if val < 0:
                self.htrOutputLineEdit.setText("0.0")
                val = 0
            if val > 3:
                self.htrOutputLineEdit.setText("3.0")
                val = 3.0
            self.htr_val = val
            self.htr_changed = True   
        except ValueError:
            self.htrOutputLineEdit.setText(str(self.htr_val))
        
        
#    def CMN_calc(self,raw_value):
#        return -4.36894/(-raw_value*1000+2.93629)

    @pyqtSignature("")
    def on_startStopButton_clicked(self):

        if self.dataThread.isStopped():    
            self.t_start = time.time()           
            self.last_time  = time.time()

            self.old_output = self.heater.measure()

#            self.pirani = MKS146C.Instrument('COM8', debug = False) #'/dev/ttyUSB0'
            
            self.data_string = "%.1f"%(time.time())
            output_file_name = IOTool.open_therm_file()
            self.output_file = open(output_file_name, 'w')
        
#            self.dataThread.initialize(None, self.CMN, self.debug) 
            self.dataThread.initialize(None, self.CMN, self.pirani, self.debug) 
            self.dataThread.start()
            
            self.startStopButton.setText("Stop")          
        else:
            self.dataThread.stop()

            self.pirani.close()
            self.output_file.close()
            
            self.startStopButton.setText("Start")   

    @pyqtSignature("")
    def on_autoScaleButton_clicked(self):
        for pw in self.plot_widgets:
            pw.check_box_x.setChecked(True)
            pw.check_box_y.setChecked(True)
            pw.rescale_and_draw()

        print ("Auto scale requested!")

    @pyqtSignature("")
    def on_manualScaleButton_clicked(self):
        for pw in self.plot_widgets:
            pw.check_box_x.setChecked(False)
            pw.check_box_y.setChecked(False)
            pw.rescale_and_draw()

        print ("Manual scale requested!")        

    def set_htr_output(self):
        self.htrOutputLineEdit.setStyleSheet("color: rgb(255, 0, 0);")
        self.htr_changed = True
        
    @pyqtSignature("")
    def on_updateButton_clicked(self):
        self.htrOutputLineEdit.setStyleSheet("color: rgb(0, 0, 0);")

        # set the heater range and current
        try:
            val = float(self.htrOutputLineEdit.text())
            
            if val < 0 or val > 100:
                self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))
            else:
                print "setting to " + str(val)
                self.heater.set_current (val * 1e-3)
        except ValueError:
            self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))
        
        self.htr_changed = False
        
    @pyqtSignature("")        
    def on_cancelButton_clicked(self):
        self.update_heater_display()
      
    
    def update_heater_display(self):
        #retrieve actual settings from instrument to fill box
        self.htr_changed = False 
        self.htrOutputLineEdit.setStyleSheet("color: rgb(0, 0, 0);")
        self.htrRangeComboBox.setStyleSheet("color: rgb(0, 0, 0);")        
        self.htrOutputLineEdit.setText(str(self.heater.measure() * 1e3))
        
        
    @pyqtSignature("")
    def on_radioButton_PID_clicked(self):
        print "in PID mode"
        # RESET THE INTEGRAL BECAUSE PID TEMPERATURE LIKELY CHANGED!
        self.integral = 0
        self.derivative = 0
        self.damping_factor = float(self.dampingLineEdit.text())
        self.PID_mode = True
        
    @pyqtSignature("")
    def on_radioButton_Man_clicked(self):
        print "In manual mode"
        self.PID_mode = False 

    @pyqtSignature("")        
    def on_updatePIDButton_clicked(self):
        self.update_setpoint(float(self.PIDLineEdit.text()))
        
    def update_setpoint(self, new_setpoint):
        print new_setpoint
        new_setpoint = float(new_setpoint)
        if new_setpoint < 510 and new_setpoint >= 0:
            self.setpoint = float(new_setpoint)
            #self.integral = 0
            #seff.derivative = 0

        self.PIDLineEdit.setText(str(self.setpoint))
        self.K_p = float(self.proportionalLineEdit.text())
        self.K_i = float(self.integralLineEdit.text())
        self.damping_factor = float(self.dampingLineEdit.text())
        
        print self.K_p, self.K_i

    def update_damping(self, damping_factor):
        print "Damping changed to: ", damping_factor
        self.damping_factor = float(damping_factor)
        self.dampingLineEdit.setText(str(damping_factor))

    #change the x axis scale to linear if it was log and reverse
    def set_Xaxis_scale(self,axis):
        curscale=axis.get_xscale()
#        print curscale
        if curscale=='log':
            axis.set_xscale('linear')
        elif curscale=='linear':
            axis.set_xscale('log')
           
    #change the y axis scale to linear if it was log and reverse
    def set_Yaxis_scale(self,axis):
        curscale=axis.get_yscale()
#        print curscale
        if curscale=='log':
            axis.set_yscale('linear')
        elif curscale=='linear':
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

        
         
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = FridgeMonitorWindow()
    #form.connect(form, SIGNAL("found"), found)
    #form.connect(form, SIGNAL("notfound"), nomore)
    #form.plot([0,1,2,3,4], [0,1,2,3,])
    form.show()
    app.exec_()



#    def main_loop(self):
#     
#        CMN_cr = cr.cr(8,"CMN", '.-b')
#        
#        active_channels = ([[1,cr.cr(1,'1K pot')],[2,cr.cr(3, 'Still','.-g')],
#                        [3,cr.cr(5, 'ICP','.-r')], [4,cr.cr(7, 'MC','.-k')],
#                        [5,cr.cr(2, 'Mats','.-c')],[9,cr.cr(4, 'Cold Plate','.-m')]])
#        
#        out_file, out_file_name = config_file_reader.open_therm_file()
#        self.fileNameLineEdit.setText(out_file_name)
#
#        t_start = time.time()
#        out_file.write("#T_start = " + str(t_start))
#        #out_file.write("
#        TIME_STEP = 10
#
#        for chan in active_channels:
#            #ax = chan[1].learn_axes(fig,4,2)
#            if chan[1].subplot_num == 1:    
#                ax = self.mplwidget.axes
#                fig = self.mplwidget.figure
#            elif chan[1].subplot_num == 2:    
#                ax = self.mplwidget_2.axes
#                fig = self.mplwidget_2.figure 
#            elif chan[1].subplot_num == 3:    
#                ax = self.mplwidget_3.axes
#                fig = self.mplwidget_3.figure 
#            elif chan[1].subplot_num == 4:    
#                ax = self.mplwidget_4.axes
#                fig = self.mplwidget_4.figure 
#            elif chan[1].subplot_num == 5:    
#                ax = self.mplwidget_5.axes
#                fig = self.mplwidget_5.figure 
#            elif chan[1].subplot_num == 6:    
#                ax = self.mplwidget_6.axes
#                fig = self.mplwidget_6.figure 
#            elif chan[1].subplot_num == 7:    
#                ax = self.mplwidget_7.axes
#                fig = self.mplwidget_7.figure 
#            elif chan[1].subplot_num == 8:    
#                ax = self.mplwidget_8.axes
#                fig = self.mplwidget_8.figure     
#                
#            chan[1].set_axes(fig, ax)
#            
#            ax.tick_params(axis='x', labelsize=8)
#            ax.tick_params(axis='y', labelsize=8)
#            fig.subplots_adjust(left = 0.15, right = 0.99)
#            #ax.set_ylabel ("test")
#            fig.canvas.draw()
#            
#        #ax = CMN_cr.learn_axes(fig,4,2)
#        ax = self.mplwidget_6.axes
#        fig = self.mplwidget_6.figure 
#        CMN_cr.set_axes(fig, ax)
#        
#        ax.tick_params(axis='x', labelsize=8)
#        ax.tick_params(axis='y', labelsize=8)                
#        
#        warning1_sent=False
#        warning2_sent=False
#        t_warning = 0
#        
#        times = np.array([])
#    
#    
#        while (self.running):
#            t_current = time.time() - t_start
#            
#            times = np.append(times,t_current)
#            stri = "%.1f, "%(t_current)
#            
#            CMN.trigger()
#            
#            for idx, chan in enumerate(active_channels):
#                lakeshore.scanner_to_channel(chan[0])
#                time.sleep(TIME_STEP)
#                dat = lakeshore.read_channel(chan[0])
#                stri += "%.3f, "%dat            
#                chan[1].add_point(t_current, dat)                
#
#                if self.htr_changed:
#                    lakeshore.set_heater_range(self.htr_range)
#                    lakeshore.set_heater_output(self.htr_val)                
#                    self.htr_changed = False                       
#                
#                if self.running == False:
#                    break
#            
#            CMN_temp = CMN.read_data()
#            CMN_stri = "%.6f, %.3f"%(CMN_temp*1000, self.CMN_calc(CMN_temp))                 
#            CMN_cr.add_point(t_current, self.CMN_calc(CMN_temp))
#            
#            stri += CMN_stri + str(self.htr_range) + ", " + str(self.htr_val) + "\n"
#            
#            print(stri)
#            out_file.write(stri)
#         
#        out_file.close()
#        lakeshore.close()
#        pirani.close()
#        
#        print "finished"
