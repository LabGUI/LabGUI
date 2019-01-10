# -*- coding: utf-8 -*-
"""
Created on Thu Mar 06 14:07:29 2014
Phoenix L300 Leak Detector
@author: PF
"""

#import visa
import random
try:
    from . import Tool
except:
    import Tool
param = {'FLOW': 'mbarl/s', 'P1': 'mbar'}

INTERFACE = Tool.INTF_SERIAL


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'PL300', debug=debug,
                                         interface=INTERFACE,
                                         baud_rate=19200, **kwargs)
        if not self.DEBUG:
            self.connection.delay = 0.25

#------------------------------------------------------------------------------

    def measure(self, channel='FLOW'):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'FLOW':
                    answer = self.ask('*READ:MBAR*L/S?')
                else:
                    answer = self.ask('*MEAS:P1:MBAR?')
                answer = float(answer)
            else:
                answer = 100 * random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def get_status(self):
        return self.ask('STAT?')


if (__name__ == '__main__'):

    myInst = Instrument("COM6")
    print(myInst.measure("FLOW"))
