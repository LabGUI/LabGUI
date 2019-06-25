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
else:
    from PyQt4 import QtCore
    from PyQt4 import QtGui

import socket
import time
import sys


class DataServer(QtCore.QThread):
    if USE_PYQT5:
        setpoint_change = QtCore.pyqtSignal(object)
        damping_change = QtCore.pyqtSignal(object)
        htr_range_change = QtCore.pyqtSignal(object)
        htr_val_change = QtCore.pyqtSignal(object)
    def __init__(self, mutex, parent=None):
        super(DataServer, self).__init__(parent)
        self.mutex = mutex
        self.channels = parent.channels
    def run(self):
        self.stopped = False
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        serversocket.bind(('localhost', 4589))
        serversocket.listen(5)
        
        while not self.stopped:
            #accept connections from outside
            (clientsocket, address) = serversocket.accept()
            #now do something with the clientsocket
            #in this case, we'll pretend this is a threaded server
            #ct = client_thread(clientsocket)
            #ct.run()
            while 1:
                try:
                    req = clientsocket.recv(1024)
                    if req:
                        self.mutex.lock()
                        # make sure to check CMN before CMN_T etc. 
                        for line in req.split('\n'):
                            print(line)
                            if line.find('LS1') != -1:
                                clientsocket.send(("LS1="+str(self.channels['LS_1']['last']) + '\n').encode())
                            elif line.find('LS2')!= -1:
                                clientsocket.send("LS2="+str(self.channels['LS_2']['last']) + '\n')
                            elif line.find('LS3')!= -1:
                                clientsocket.send("LS3="+str(self.channels['LS_3']['last']) + '\n')
                            elif line.find('LS4')!= -1:
                                clientsocket.send("LS4="+str(self.channels['LS_4']['last']) + '\n')  
                            elif line.find('LS5')!= -1:
                                clientsocket.send("LS5="+str(self.channels['LS_5']['last']) + '\n') 
                            elif line.find('LS9')!= -1:
                                clientsocket.send("LS9="+str(self.channels['LS_9']['last']) + '\n') 
                            elif line.find('CMN_T')!= -1:
                                clientsocket.send("CMN="+str(self.channels['CMN']['last_T']) + '\n')
                            elif line.find('CMN')!= -1:
                                clientsocket.send("CMN="+str(self.channels['CMN']['last']) + '\n')                              

                            elif line.find('SETP') != -1:
                                print("Changing temperature setpoint! " + line)
                                if USE_PYQT5:
                                    self.setpoint_change.emit(line.split()[-1].strip())
                                else:
                                    self.emit(SIGNAL("setpoint_change(PyQt_PyObject)"), line.split()[-1].strip())

                            elif line.find('DAMP') != -1:
                                print("Changing damping factor! " + line)
                                if USE_PYQT5:
                                    self.damping_change.emit(line.split()[-1].strip())
                                else:
                                    self.emit(SIGNAL("damping_change(PyQt_PyObject)"), line.split()[-1].strip())
                           
                            elif line.find('SET_HTR_RANGE') != -1:
                                print("Changing heater range! " + line)
                                if USE_PYQT5:
                                    self.htr_range_change.emit(line.split()[-1].strip())
                                else:
                                    self.emit(SIGNAL("htr_range_change(PyQt_PyObject)"), line.split()[-1].strip())
                           
                            elif line.find('SET_HTR_VAL') != -1:
                                print("Changing heater value! " + line)
                                if USE_PYQT5:
                                    self.htr_val_change.emit(line.split()[-1].strip())
                                else:
                                    self.emit(SIGNAL("htr_val_change(PyQt_PyObject)"), line.split()[-1].strip())
                                
                        self.mutex.unlock()
                    else:
                        break
                except IOError:
                    break
                except:
                    print(sys.exc_info())
        self.stopped = True
        self.completed = False
    
    def stop(self):
        self.stopped = True

    def isStopped(self):
        return self.stopped

# this version no longer called by FridgeClient.py
def get_fridge_data(data_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        s.connect(('localhost', 4589))
     
        s.send((data_name + '?\n').encode())
        
        stri = s.recv(1024)
        dat = float(stri.split('=')[-1].strip())
        s.close()
        
        return dat
        
    except IOError:
        print("connection to fridge monitor failed")
        return 0
    except:
        print(sys.exc_info())
# this version no longer called by FridgeClient.py
def change_setpoint(val):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        s.connect(('localhost', 4589))
     
        s.send(('SETP ' + str(val) + '\n').encode())

        s.close()

        
    except IOError:
        print("connection to fridge monitor failed")
        return 0

    except:
        print(sys.exc_info())
		
