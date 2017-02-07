# -*- coding: utf-8 -*-
"""
Created on Tue May 22 09:51:19 2012
Driver for DAC488
@author: Bram
"""

try:
    from . import Tool
except:
    import Tool
    
import time

param = {'': ''}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'DAC488', debug=debug, 
                                         interface = INTERFACE, **kwargs)
        
        if not self.DEBUG:
            #            self.name = instrument(name)
            self.currentVoltage = 0
            # does something
            self.write('*RX')
            time.sleep(2)

    def identify(self, msg=''):
        if not self.DEBUG:
            # the *IDN? is probably not working
            return msg  # +self.ask('*RX')
        else:
            return msg + self.ID_name

    def set_range(self, vrange, port=1):
        if not self.DEBUG:
            self.write('P' + str(port) + 'X')
            self.write('R' + str(vrange) + 'X')
            # vrange does not mean the literal voltage range!!!
            # 1,2,3,4 correspond to 1V, 2V, 5V, 10V bipolar

    def set_voltage(self, voltage, port=1):
        if not self.DEBUG:
            self.currentVoltage = voltage
            self.write("P" + str(port))
            self.write("V" + str(voltage))
            self.write("X")

    def error_query(self):
        if not self.DEBUG:
            return self.ask('E?X')

    def reset(self):
        if not self.DEBUG:
            self.write('DCL')
