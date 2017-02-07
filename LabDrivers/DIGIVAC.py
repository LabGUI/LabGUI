# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 12:28:29 2015
@author: pfduc
"""

import random
try:
    from . import Tool
except:
    import Tool
    

param = {'Pressure': 'Torr'}

INTERFACE = Tool.INTF_SERIAL

class Instrument(Tool.MeasInstr):
    """
    The DIGIVAC is a Rs232 connection which outputs a string every 1second, no need more than reading the output
    """

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'DIGIVAC', debug=debug, interface=INTERFACE, baud_rate=9600,
                                         term_chars="\r\n", timeout=2, bytesize=8, parity='N', stopbits=1, xonxoff=False, dsrdtr=False, **kwargs)


    def measure(self, channel='Pressure'):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'Pressure':
                    print(self.read())
                    answer = float(self.read())  # read in Torr
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer


if __name__ == "__main__":
    i = Instrument("COM4", False)
#    i.identify()
    print(i.measure())
