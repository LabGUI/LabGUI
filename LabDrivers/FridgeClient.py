# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28, 2013
"Instrument"-like implementation of a client to talk to the Fridgemonitor program
@author: Ben

"""
import socket
import numpy as np

from . import Tool
#from fridgemonitor import data_server
from collections import OrderedDict

param = OrderedDict([('LS1', 'ohms'), ('LS2', 'ohms'), ('LS3', 'ohms'), ('LS4', 'ohms'),
                     ('LS5', 'ohms'), ('LS9', 'ohms'), ('CMN', 'H'), ('CMN_T', 'mK')])

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False):
        # This instrument doesn't take any ResourceName other than FridgeServer!
        # this could later be modified to use the port number, which is currently hardcoded as 4589
        resource_name = 'FridgeServer'
        super(Instrument, self).__init__(resource_name,
                                         'FridgeClient', debug=debug, interface=INTERFACE)
        print("made a fridge client")

    # overload the connect() method so that no real connection is made
    # a client socket is generated and destroyed for each request in measure()
    def connect(self, resource_name=None):
        pass

    def measure(self, channel='LS1'):

        if not self.DEBUG:
            if channel in self.last_measure:
                answer = self.get_fridge_data(str(channel))
            else:
                print("you are trying to measure a non existent channel : " + channel)
                print("existing channels :", self.channels)
                answer = None

        else:
            answer = np.random.random()

        self.last_measure[channel] = answer
        return answer

    def get_fridge_data(self, data_name):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect(('localhost', 4589))

            s.send(data_name + '?\n')

            stri = s.recv(1024)
            dat = float(stri.split('=')[-1].strip())
            s.close()

            return dat

        except IOError:
            print("connection to fridge monitor failed")
            return 0

    def change_setpoint(self, val):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect(('localhost', 4589))

            s.send('SETP ' + str(val) + '\n')

            s.close()

        except IOError:
            print("connection to fridge monitor failed")
            return 0

    def change_damping(self, val):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect(('localhost', 4589))

            s.send('DAMP ' + str(val) + '\n')

            s.close()

        except IOError:
            print("connection to fridge monitor failed")
            return 0
