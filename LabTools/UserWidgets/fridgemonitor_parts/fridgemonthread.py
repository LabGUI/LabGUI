# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 17:42:35 2013

@author: Ben
"""
from LocalVars import USE_PYQT5
if USE_PYQT5:
    from PyQt5 import QtCore
    import PyQt5.QtWidgets as QtGui
    from PyQt5 import Qt
    QMutexLocker = QtCore.QMutexLocker
else:
    from PyQt4 import QtCore
    from PyQt4 import QtGui

#from LabDrivers import LS370
#from LabDrivers import HP4263B
#from LabDrivers import MKS
import time
import sys


class FridgeMonThread(QtCore.QThread):
    if USE_PYQT5:
        data = QtCore.pyqtSignal(object)
        finished = QtCore.pyqtSignal(bool)
    def __init__(self, mutex, parent=None):
        super(FridgeMonThread, self).__init__(parent)
        self.mutex = mutex
        
        self.stopped = True
        self.completed = False

    def initialize(self, lakeshore, CMN, pirani, debug):
        self.lakeshore = lakeshore
        self.CMN = CMN
        self.pirani = pirani
        
        self.debug = debug        
        self.active_channels = [1,2,3,4,5,9]    
        
        self.TIME_STEP = 10

    def run(self):
        try:
            self.stopped = False
            self.main_loop()
            self.stop()
            if USE_PYQT5:
                self.finished.emit(self.completed)
            else:
                self.emit(SIGNAL("finished(bool)"), self.completed)
        except:
            print(sys.exc_info())
        
    
    def stop(self):
        self.stopped = True

    def isStopped(self):
        return self.stopped
        
    def main_loop(self):
        while self.isStopped() == False:
            # split the lakeshore list in two so that CMN is read twice as fast (30 s intervals)
            
        
            if self.lakeshore == None:
                # this part is for the version with CMN only
                self.CMN.trigger()
                time.sleep(self.TIME_STEP)
                CMN_temp = self.CMN.read_data()
                if USE_PYQT5:
                    self.data.emit(['CMN', CMN_temp])
                else:
                    self.emit(SIGNAL("data(PyQt_PyObject)"), ['CMN', CMN_temp])
                pirani_pressure = self.pirani.get_pressure(2)
                if USE_PYQT5:
                    self.data.emit(['Pirani', pirani_pressure])
                else:
                    self.emit(SIGNAL("data(PyQt_PyObject)"), ['Pirani', pirani_pressure])
                

            else:    
                # This is the usual loop that cycles through lakeshore channels and also measures the CMN
               # for active in [self.active_channels[:3], self.active_channels[3:]]:
            
                # constantly read the CMN
                for chan in self.active_channels:    
                    
                    self.CMN.trigger()
                        
                    #for chan in active:
                    if True:
                        with QMutexLocker(self.mutex):
                            self.lakeshore.scanner_to_channel(chan)
                            
                        time.sleep(self.TIME_STEP)
                        
                        with QMutexLocker(self.mutex):
                            dat = self.lakeshore.read_channel(chan)
                        if USE_PYQT5:
                            self.data.emit(['LS_%d'%chan, dat])
                        else:
                            self.emit(SIGNAL("data(PyQt_PyObject)"), ['LS_%d'%chan, dat])
                        
                        while self.isStopped() == True:
                            break
                    
        #            p1 = self.pirani.get_pressure(1)
        #            p2 = self.pirani.get_pressure(2)
        #            self.emit(SIGNAL("data(PyQt_PyObject)"), ['p1', p1])
        #            self.emit(SIGNAL("data(PyQt_PyObject)"), ['p2', p2])
                    
                    CMN_temp = self.CMN.read_data()
                    if USE_PYQT5:
                        self.data.emit(['CMN', CMN_temp])
                    else:
                        self.emit(SIGNAL("data(PyQt_PyObject)"), ['CMN', CMN_temp])
                    
                    pirani_pressure1 = self.pirani.get_pressure(1)
                    if USE_PYQT5:
                        self.data.emit(['Pirani-1', pirani_pressure1])
                    else:
                        self.emit(SIGNAL("data(PyQt_PyObject)"), ['Pirani-1', pirani_pressure1])
                    pirani_pressure2 = self.pirani.get_pressure(2)
                    if USE_PYQT5:
                        self.data.emit(['Pirani-2', pirani_pressure2])
                    else:
                        self.emit(SIGNAL("data(PyQt_PyObject)"), ['Pirani-2', pirani_pressure2])


    def clean_up(self):
        pass
