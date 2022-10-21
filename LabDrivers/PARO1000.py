# -*- coding: utf-8 -*-
"""
Created on Wed May 08 13:31:59 2013
Paroscientific Digiquartz Pressure sensor 1000 Driver
@author: PF
"""

import random
try:
    from . import Tool
except:
    import Tool

param = {'PRESSURE': 'psi', 'TEMPERATURE': 'C'}

INTERFACE = Tool.INTF_SERIAL


class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False, **kwargs):

        # manage the presence of the keyword interface which will determine
        # which method of communication protocol this instrument will use
        if 'interface' in kwargs.keys():

            interface = kwargs.pop('interface')

        else:

            interface = INTERFACE

        super(Instrument, self).__init__(resource_name,
                                         'PARO1000', debug=debug,
                                         interface=interface,
                                         term_chars='\r\n', **kwargs)

    def measure(self, channel='PRESSURE'):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'PRESSURE':
                    command = '*0100P3'
                elif channel == 'TEMPERATURE':
                    command = '*0100Q3'
                answer = (self.ask(command))
                print(answer)
                answer = float(answer[5:])  # remove the first 5 characters
            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def identify(self, msg=''):
        if not self.DEBUG:

            answer = self.ask('*0100MN')
            answer = "PARO" + answer[8:]

        else:

            answer = self.ID_name

        return msg + answer


if __name__ == "__main__":
    i = Instrument("COM4")
    print(i.identify())
